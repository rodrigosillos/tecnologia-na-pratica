# syntax=docker/dockerfile:1
FROM node:24-bookworm-slim
RUN --mount=type=secret,id=exemplo,required=true \
    test -s /run/secrets/exemplo
USER node
CMD ["node", "--version"]
