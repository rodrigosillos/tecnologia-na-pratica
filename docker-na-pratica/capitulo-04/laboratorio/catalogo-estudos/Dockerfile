FROM node:24-bookworm-slim
WORKDIR /app
COPY app.js ./
RUN node --check app.js
COPY index.html temas.json ./
USER node
EXPOSE 3000
CMD ["node", "app.js"]
