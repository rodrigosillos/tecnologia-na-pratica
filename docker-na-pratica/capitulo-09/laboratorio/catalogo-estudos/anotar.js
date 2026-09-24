'use strict';
const { lerAnotacoes, adicionarAnotacao } = require('./armazenamento');
try {
  const argumentos = process.argv.slice(2);
  if (argumentos.length !== 1) {
    throw new Error('Uso: node anotar.js "texto" ou node anotar.js --listar');
  }
  const notas = argumentos[0] === '--listar'
    ? lerAnotacoes()
    : adicionarAnotacao(argumentos[0]);
  console.log(JSON.stringify(notas));
} catch (erro) {
  console.error(`Falha nas anotacoes: ${erro.code ?? 'DADOS'}: ${erro.message}`);
  process.exitCode = 1;
}
