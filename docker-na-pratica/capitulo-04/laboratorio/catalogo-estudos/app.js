'use strict';
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');

const arquivos = new Map([
  ['/', ['index.html', 'text/html; charset=utf-8']],
  ['/api/temas', ['temas.json', 'application/json; charset=utf-8']]
]);

const servidor = http.createServer((req, res) => {
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('X-Content-Type-Options', 'nosniff');
  let caminho;
  try {
    caminho = new URL(req.url, 'http://localhost').pathname;
  } catch {
    res.writeHead(400);
    return res.end('Requisicao invalida.');
  }
  console.log(JSON.stringify({ metodo: req.method, caminho }));
  if (req.method !== 'GET') {
    res.writeHead(405, { Allow: 'GET' });
    return res.end('Metodo nao permitido.');
  }
  if (caminho === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    return res.end(JSON.stringify({ status: 'ok' }));
  }
  const arquivo = arquivos.get(caminho);
  if (!arquivo) {
    res.writeHead(404);
    return res.end('Rota nao encontrada.');
  }
  fs.readFile(path.join(__dirname, arquivo[0]), (erro, dados) => {
    if (erro) {
      console.error(erro.message);
      res.writeHead(500);
      return res.end('Falha ao ler arquivo da aplicacao.');
    }
    res.writeHead(200, { 'Content-Type': arquivo[1] });
    res.end(dados);
  });
});

servidor.on('error', (erro) => {
  console.error(erro.message);
  process.exitCode = 1;
});
servidor.listen(3000, '0.0.0.0', () => {
  console.log('Catalogo de Estudos: porta 3000.');
});
for (const sinal of ['SIGTERM', 'SIGINT']) {
  process.on(sinal, () => {
    console.log(`Encerrando: ${sinal}`);
    const limite = setTimeout(() => process.exit(1), 5000);
    limite.unref();
    servidor.close(() => {
      clearTimeout(limite);
      process.exit(0);
    });
  });
}
