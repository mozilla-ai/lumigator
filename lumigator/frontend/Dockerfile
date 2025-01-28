ARG NODE_VERSION=18.20.0

FROM node:${NODE_VERSION}-alpine AS base

# Copy the project into the image
COPY . /mzai/frontend

WORKDIR /mzai/

# Install dependencies
RUN npm --prefix /mzai/frontend install

# Build static files
RUN npm --prefix /mzai/frontend run build

FROM nginx:1.27.2-alpine-slim AS server

# Copy built files to the Nginx image
COPY --from=base /mzai/frontend/dist /usr/share/nginx/html

EXPOSE 80
