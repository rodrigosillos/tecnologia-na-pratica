'use strict';
const porta = process.env.PORT ?? '3000';
const url = process.argv[2] ?? `http://127.0.0.1:${porta}/health`;
fetch(url, { signal: AbortSignal.timeout(3000) })
  .then(async (resposta) => {
    console.log(`HTTP ${resposta.status}`);
    console.log(await resposta.text());
    if (!resposta.ok) process.exitCode = 1;
  })
  .catch((erro) => {
    console.error(`Falha HTTP: ${erro.cause?.code ?? erro.name}`);
    process.exitCode = 1;
  });
