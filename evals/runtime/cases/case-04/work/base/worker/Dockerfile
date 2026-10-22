FROM node:24.22.0-bookworm-slim@sha256:e37b89c5afa36c913b91c070df40f185b7fd55d32daaac4398396131a9d12487 AS build
WORKDIR /srv
COPY package.json .
COPY src ./src

FROM node:24.22.0-bookworm-slim@sha256:e37b89c5afa36c913b91c070df40f185b7fd55d32daaac4398396131a9d12487
WORKDIR /srv
COPY --from=build /srv /srv
USER node
CMD ["node", "src/server.js"]
