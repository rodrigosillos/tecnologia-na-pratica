'use strict';
const fs = require('node:fs');
const path = require('node:path');
const { randomUUID } = require('node:crypto');

function diretorioDados() {
  const dir = process.env.DATA_DIR ?? path.join(__dirname, 'dados');
  if (!dir.trim() || !path.isAbsolute(dir)) {
    throw new Error('DATA_DIR deve ser um caminho absoluto nao vazio.');
  }
  if (!fs.statSync(dir).isDirectory()) {
    throw new Error('DATA_DIR deve apontar para um diretorio existente.');
  }
  return dir;
}

function lerAnotacoes() {
  const arquivo = path.join(diretorioDados(), 'anotacoes.json');
  let texto;
  try {
    if (fs.statSync(arquivo).size > 262144) {
      throw new Error('Arquivo excede o limite de 256 KiB do laboratorio.');
    }
    texto = fs.readFileSync(arquivo, 'utf8');
  } catch (erro) {
    if (erro.code === 'ENOENT') return [];
    throw erro;
  }
  const notas = JSON.parse(texto);
  const valida = (nota) => typeof nota === 'string' &&
    nota.trim().length > 0 && nota.length <= 240;
  if (!Array.isArray(notas) || notas.length > 100 || !notas.every(valida)) {
    throw new Error('Anotacoes devem ser ate 100 textos de 1 a 240 caracteres.');
  }
  return notas;
}

function adicionarAnotacao(texto) {
  const nota = typeof texto === 'string' ? texto.trim() : '';
  if (!nota || nota.length > 240) {
    throw new Error('Informe uma anotacao de 1 a 240 caracteres.');
  }
  const notas = lerAnotacoes();
  if (notas.length >= 100) throw new Error('Limite de 100 anotacoes atingido.');
  notas.push(nota);
  const dir = diretorioDados();
  const destino = path.join(dir, 'anotacoes.json');
  const temporario = path.join(dir, `.anotacoes-${randomUUID()}.tmp`);
  let criado = false;
  try {
    fs.writeFileSync(temporario, JSON.stringify(notas, null, 2) + '\n', {
      encoding: 'utf8', flag: 'wx', mode: 0o600
    });
    criado = true;
    fs.renameSync(temporario, destino);
  } finally {
    if (criado && fs.existsSync(temporario)) fs.unlinkSync(temporario);
  }
  return notas;
}

module.exports = { diretorioDados, lerAnotacoes, adicionarAnotacao };
