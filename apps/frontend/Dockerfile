# Build context must be the monorepo root — the frontend imports packages/ui
# directly from source (see vite.config.ts aliases), not as a built package.

FROM node:20-alpine AS build
WORKDIR /repo

COPY package.json yarn.lock ./
COPY apps/frontend/package.json apps/frontend/package.json
COPY apps/browser-extension/package.json apps/browser-extension/package.json
COPY apps/website/package.json apps/website/package.json
COPY packages/ui/package.json packages/ui/package.json
RUN yarn install --frozen-lockfile

COPY apps/frontend apps/frontend
COPY packages/ui packages/ui

ARG VITE_API_BASE_URL=http://localhost:8000/api/v1
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN yarn workspace frontend build

FROM nginx:alpine
COPY apps/frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /repo/apps/frontend/dist /usr/share/nginx/html
EXPOSE 80
