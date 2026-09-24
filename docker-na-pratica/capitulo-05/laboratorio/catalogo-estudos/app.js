'use strict';
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');

function lerConfiguracao() {
  const textoPorta = process.env.PORT ?? '3000';
  const porta = Number(textoPorta);
  const host = process.env.HOST ?? '0.0.0.0';
  const ambiente = process.env.APP_ENV ?? 'desenvolvimento';
  if (!/^\d+$/.test(textoPorta) || !Number.isInteger(porta) ||
      porta < 1024 || porta > 65535) {
    throw new Error('PORT deve ser um inteiro entre 1024 e 65535.');
  }
  if (!['0.0.0.0', '127.0.0.1'].includes(host)) {
    throw new Error('HOST deve ser 0.0.0.0 ou 127.0.0.1 neste laboratorio.');
  }
  if (!['desenvolvimento', 'homologacao', 'producao'].includes(ambiente)) {
    throw new Error('APP_ENV deve ser desenvolvimento, homologacao ou producao.');
  }
  return { porta, host, ambiente };
}

function iniciar() {
  let config;
  try {
    config = lerConfiguracao();
  } catch (erro) {
    console.error(`Configuracao invalida: ${erro.message}`);
    process.exitCode = 1;
    return;
  }
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
    if (caminho === '/health' || caminho === '/api/config') {
      const resposta = caminho === '/health'
        ? { status: 'ok' }
        : { ambiente: config.ambiente, porta: config.porta };
      res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
      return res.end(JSON.stringify(resposta));
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
    console.error(`Falha ao iniciar: ${erro.code ?? 'ERRO'}: ${erro.message}`);
    process.exitCode = 1;
  });
  servidor.listen(config.porta, config.host, () => {
    console.log(JSON.stringify({ evento: 'inicio', pid: process.pid, ...config }));
  });
  let encerrando = false;
  for (const sinal of ['SIGTERM', 'SIGINT']) {
    process.on(sinal, () => {
      if (encerrando) return;
      encerrando = true;
      console.log(`Encerrando: ${sinal}`);
      const limite = setTimeout(() => process.exit(1), 5000);
      limite.unref();
      servidor.close(() => {
        clearTimeout(limite);
        process.exitCode = 0;
      });
    });
  }
}

iniciar();
