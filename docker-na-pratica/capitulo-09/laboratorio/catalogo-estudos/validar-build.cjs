"use strict";
const fs = require("node:fs");
const { createHash } = require("node:crypto");
const arquivos = [
  "app.js", "diagnostico.js", "armazenamento.js", "anotar.js",
  "index.html", "temas.json"
];
try {
  fs.rmSync("verificacao.json", { force: true });
  const temas = JSON.parse(fs.readFileSync("temas.json", "utf8"));
  if (!Array.isArray(temas) || temas.length === 0 ||
      temas.some(t => !t || !Number.isSafeInteger(t.id) || t.id < 1 ||
        typeof t.nome !== "string" || !t.nome.trim()) ||
      new Set(temas.map(t => t.id)).size !== temas.length) {
    throw new Error("Temas devem ter IDs positivos unicos e nomes nao vazios.");
  }
  const pagina = fs.readFileSync("index.html", "utf8");
  if (!pagina.includes("/api/temas") || !pagina.includes("/api/anotacoes")) {
    throw new Error("A pagina deve preservar os caminhos das APIs do catalogo.");
  }
  const sha256 = {};
  for (const arquivo of arquivos) {
    sha256[arquivo] = createHash("sha256")
      .update(fs.readFileSync(arquivo)).digest("hex");
  }
  fs.writeFileSync("verificacao.json", JSON.stringify({
    escopo: "Estrutura de temas, caminhos no HTML e hashes dos arquivos.",
    quantidadeTemas: temas.length, sha256
  }, null, 2) + "\n");
  console.log("Verificacao de build concluida.");
} catch (erro) {
  console.error(`Falha na verificacao de build: ${erro.message}`);
  process.exitCode = 1;
}
