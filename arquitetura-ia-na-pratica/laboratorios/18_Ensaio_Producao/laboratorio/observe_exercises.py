from observability import percentile,burn_rate,histogram,merge_histograms


def page_decision(long_window,short_window,threshold=6,min_requests=100):
    rates=[burn_rate(bad,n) for bad,n in (long_window,short_window)]
    if any(rate is None for rate in rates):return 'no_data'
    if any(n<min_requests for _,n in (long_window,short_window)):
        return 'insufficient_volume'
    return 'page' if all(rate>=threshold for rate in rates) else 'observe'


def exercise25():
    group_a=[10]*19+[1000]
    group_b=[100]*20
    local=[percentile(g,.95) for g in (group_a,group_b)]
    pooled=group_a+group_b
    return {'local_p95':local,'wrong_average':sum(local)/2,
            'pooled_p95':percentile(pooled,.95),
            'pooled_p99':percentile(pooled,.99),
            'histogram':merge_histograms([
                histogram(group_a),histogram(group_b)])}


def exercise26():
    first=((30,1000),(10,100))
    sustained=((60,1000),(10,100))
    return {'first_rates':[burn_rate(*x) for x in first],
            'first_decision':page_decision(*first),
            'sustained_rates':[burn_rate(*x) for x in sustained],
            'sustained_decision':page_decision(*sustained),
            'low_volume':page_decision((1,10),(1,10)),
            'no_traffic':page_decision((0,0),(0,0))}


if __name__=='__main__':
    import json
    from pathlib import Path
    result={'exercise25':exercise25(),'exercise26':exercise26()}
    Path('results').mkdir(exist_ok=True)
    Path('results/exercises.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
