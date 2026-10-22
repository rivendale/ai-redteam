FROM node:22.23.1-bookworm-slim@sha256:a5c4bd28830be89d3b3c0c7c11a50cd3f1db03412217c89d3c63808be5339960 AS build
WORKDIR /srv
COPY package.json .
COPY src ./src

FROM node:22.23.1-bookworm-slim@sha256:a5c4bd28830be89d3b3c0c7c11a50cd3f1db03412217c89d3c63808be5339960
WORKDIR /srv
COPY --from=build /srv /srv
USER node
CMD ["node", "src/server.js"]
