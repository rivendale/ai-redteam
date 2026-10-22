FROM node:22.23.3-bookworm-slim@sha256:785ddfe3b9ff258f242cef929b4ba23800cb4b344e4a6a9501434d44861ef963 AS build
WORKDIR /srv
COPY package.json .
COPY src ./src

FROM node:22.23.3-bookworm-slim@sha256:785ddfe3b9ff258f242cef929b4ba23800cb4b344e4a6a9501434d44861ef963
WORKDIR /srv
COPY --from=build /srv /srv
USER node
CMD ["node", "src/server.js"]
