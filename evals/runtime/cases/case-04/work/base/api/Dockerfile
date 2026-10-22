FROM node:22.23.4-bookworm-slim@sha256:70148cd3df6a7bfe1a2128403a10c748863ee8742aed72784b42f20cc764b72f AS build
WORKDIR /srv
COPY package.json .
COPY src ./src

FROM node:22.23.4-bookworm-slim@sha256:70148cd3df6a7bfe1a2128403a10c748863ee8742aed72784b42f20cc764b72f
WORKDIR /srv
COPY --from=build /srv /srv
USER node
CMD ["node", "src/server.js"]
