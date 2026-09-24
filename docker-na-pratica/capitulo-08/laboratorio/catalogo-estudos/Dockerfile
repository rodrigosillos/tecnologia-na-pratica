FROM node:24-bookworm-slim
WORKDIR /app
COPY app.js diagnostico.js armazenamento.js anotar.js ./
RUN node --check app.js && node --check diagnostico.js \
    && node --check armazenamento.js && node --check anotar.js
COPY index.html temas.json ./
RUN mkdir -p /app/dados \
    && printf '[]\n' > /app/dados/anotacoes.json \
    && chown -R node:node /app/dados \
    && chmod 700 /app/dados && chmod 600 /app/dados/anotacoes.json
USER node
EXPOSE 3000
CMD ["node", "app.js"]
