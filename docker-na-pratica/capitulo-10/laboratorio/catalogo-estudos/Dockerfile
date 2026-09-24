FROM node:24-bookworm-slim AS base
WORKDIR /app

FROM base AS verificacao
COPY app.js diagnostico.js armazenamento.js anotar.js ./
RUN node --check app.js && node --check diagnostico.js \
    && node --check armazenamento.js && node --check anotar.js
COPY index.html temas.json validar-build.cjs ./
RUN node validar-build.cjs

FROM base AS execucao
RUN mkdir -p /app/dados \
    && printf '[]\n' > /app/dados/anotacoes.json \
    && chown -R node:node /app/dados \
    && chmod 700 /app/dados && chmod 600 /app/dados/anotacoes.json
COPY --from=verificacao /app/app.js /app/diagnostico.js ./
COPY --from=verificacao /app/armazenamento.js /app/anotar.js ./
COPY --from=verificacao /app/index.html /app/temas.json ./
USER node
EXPOSE 3000
CMD ["node", "app.js"]
