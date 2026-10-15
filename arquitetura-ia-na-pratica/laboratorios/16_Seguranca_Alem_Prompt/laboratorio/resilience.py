"""Deterministic, single-threaded resilience simulator. No network or sleep."""
from dataclasses import dataclass
from random import Random
from threading import Event


def integer(value, name, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(name)
    return value


class Clock:
    def __init__(self, now=0, after_advance=None):
        self.now = integer(now, 'now')
        self.after_advance = after_advance

    def advance(self, milliseconds):
        self.now += integer(milliseconds, 'milliseconds')
        if self.after_advance:
            self.after_advance(self.now)


@dataclass(frozen=True)
class Policy:
    budget_ms: int = 1200
    attempt_ms: int = 300
    reserve_ms: int = 100
    minimum_ms: int = 50
    max_attempts: int = 3
    base_ms: int = 100
    cap_ms: int = 400

    def __post_init__(self):
        for name in ('budget_ms', 'attempt_ms', 'minimum_ms',
                     'max_attempts', 'base_ms', 'cap_ms'):
            integer(getattr(self, name), name, 1)
        integer(self.reserve_ms, 'reserve_ms')
        if self.attempt_ms < self.minimum_ms:
            raise ValueError('attempt smaller than minimum')
        if self.cap_ms < self.base_ms:
            raise ValueError('cap smaller than base')


@dataclass(frozen=True)
class Step:
    duration_ms: int
    status: str = 'ok'
    retry_after_ms: int = 0

    def __post_init__(self):
        integer(self.duration_ms, 'duration_ms')
        integer(self.retry_after_ms, 'retry_after_ms')
        if self.status not in {'ok', '503', '429', '400', 'invalid'}:
            raise ValueError('unknown scripted status')


class ScriptedProvider:
    def __init__(self, steps):
        self.steps = list(steps)
        self.calls = 0

    def invoke(self, clock, allowance):
        if self.calls >= len(self.steps):
            raise RuntimeError('script exhausted; fix the experiment')
        step = self.steps[self.calls]
        self.calls += 1
        clock.advance(min(step.duration_ms, allowance))
        if step.duration_ms >= allowance:
            return 'timeout', 0
        return step.status, step.retry_after_ms


class RetryBudget:
    """Finite retry permits, shared deliberately; not a rate limiter."""
    def __init__(self, tokens=2):
        self.tokens = integer(tokens, 'tokens')

    def take(self):
        if self.tokens == 0:
            return False
        self.tokens -= 1
        return True


class CircuitOpen(RuntimeError):
    pass


@dataclass(frozen=True)
class Permit:
    ticket: int
    generation: int
    probe: bool


class CircuitBreaker:
    """One local dependency scope; no thread or process synchronization."""
    def __init__(self, threshold=3, cooldown_ms=500):
        self.threshold = integer(threshold, 'threshold', 1)
        self.cooldown_ms = integer(cooldown_ms, 'cooldown_ms', 1)
        self.state = 'closed'
        self.failures = 0
        self.open_until = 0
        self.generation = 0
        self.serial = 0
        self.inflight = {}

    def acquire(self, now):
        integer(now, 'now')
        if self.state == 'open':
            if now < self.open_until:
                raise CircuitOpen('cooldown')
            self.state = 'half_open'
            self.generation += 1
            probe = True
        elif self.state == 'half_open':
            raise CircuitOpen('probe in flight')
        else:
            probe = False
        self.serial += 1
        permit = Permit(self.serial, self.generation, probe)
        self.inflight[permit.ticket] = permit
        return permit

    def _open(self, now):
        self.state = 'open'
        self.open_until = now + self.cooldown_ms
        self.generation += 1

    def finish(self, permit, health, now):
        integer(now, 'now')
        if health not in {'healthy', 'unhealthy', 'neutral'}:
            raise ValueError('health')
        if self.inflight.get(permit.ticket) is not permit:
            raise ValueError('unknown or already consumed permit')
        del self.inflight[permit.ticket]
        if permit.generation != self.generation:
            return  # Old completions cannot heal a newer open circuit.
        if permit.probe:
            if health == 'healthy':
                self.state = 'closed'
                self.failures = 0
                self.generation += 1
            else:
                self._open(now)
        elif health == 'healthy':
            self.failures = 0
        elif health == 'unhealthy':
            self.failures += 1
            if self.failures >= self.threshold:
                self._open(now)


def attempt_allowance(deadline, now, policy):
    remaining = deadline - now - policy.reserve_ms
    if remaining < policy.minimum_ms:
        return 0
    return min(policy.attempt_ms, remaining)


def retry_delay(retry_number, policy, rng, retry_after_ms=0):
    integer(retry_number, 'retry_number', 1)
    integer(retry_after_ms, 'retry_after_ms')
    window = policy.base_ms
    for _ in range(retry_number - 1):
        if window >= policy.cap_ms:
            break
        window = min(policy.cap_ms, window * 2)
    return max(rng.randint(0, window), retry_after_ms)


def health_of(status):
    if status == 'ok':
        return 'healthy'
    if status in {'503', 'timeout'}:
        return 'unhealthy'
    return 'neutral'


class Controller:
    def __init__(self, clock, policy=None, breaker=None,
                 retries=None, seed=7):
        self.clock = clock
        self.policy = policy or Policy()
        self.breaker = breaker or CircuitBreaker()
        self.retries = retries if retries is not None else RetryBudget()
        self.rng = Random(seed)
        self.started = clock.now
        self.deadline = self.started + self.policy.budget_ms

    def run(self, provider, cancel=None, read_only=True):
        if type(read_only) is not bool:
            raise ValueError('read_only')
        cancel = cancel if cancel is not None else Event()
        attempts, waits, trace = 0, [], []
        started = self.clock.now

        def result(reason):
            return dict(reason=reason, attempts=attempts,
                        elapsed_ms=self.clock.now-started,
                        operation_elapsed_ms=self.clock.now-self.started,
                        waits_ms=waits, circuit=self.breaker.state,
                        retry_tokens=self.retries.tokens, trace=trace)

        while True:
            if cancel.is_set():
                return result('cancelled')
            allowance = attempt_allowance(
                self.deadline, self.clock.now, self.policy)
            if allowance == 0:
                return result('deadline')
            if attempts and self.retries.tokens == 0:
                return result('retry_budget')
            try:
                permit = self.breaker.acquire(self.clock.now)
            except CircuitOpen:
                return result('circuit_open')
            if attempts:
                assert self.retries.take()
            attempts += 1
            try:
                status, retry_after = provider.invoke(
                    self.clock, allowance)
            except Exception:
                self.breaker.finish(permit, 'neutral', self.clock.now)
                raise  # Programming errors are not transient failures.
            if cancel.is_set():
                self.breaker.finish(permit, 'neutral', self.clock.now)
                return result('cancelled')
            self.breaker.finish(permit, health_of(status), self.clock.now)
            trace.append(dict(attempt=attempts, status=status,
                              allowance_ms=allowance, at_ms=self.clock.now))
            if status == 'ok':
                return result('success')
            if status not in {'503', '429', 'timeout'}:
                return result('non_retryable')
            if not read_only:
                return result('unsafe_to_retry')
            if attempts >= self.policy.max_attempts:
                return result('attempt_limit')
            if self.breaker.state == 'open':
                return result('circuit_open')
            if self.retries.tokens == 0:
                return result('retry_budget')
            wait = retry_delay(attempts, self.policy,
                               self.rng, retry_after)
            remaining = self.deadline - self.clock.now
            needed = wait + self.policy.minimum_ms + self.policy.reserve_ms
            if needed > remaining:
                return result('deadline')
            waits.append(wait)
            self.clock.advance(wait)


class ControlledFailure(RuntimeError):
    """Internal reason; Chapter 8 redacts it at the public boundary."""

