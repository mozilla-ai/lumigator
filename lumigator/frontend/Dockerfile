ARG NODE_VERSION=18.20.0

FROM node:${NODE_VERSION}-alpine AS base

# Copy the project into the image
COPY ../../ /mzai

WORKDIR /mzai/

# Install dependencies
RUN npm --prefix /mzai/lumigator/frontend install

# Build static files
RUN npm --prefix /mzai/lumigator/frontend run build


FROM nginx:1.27.2-alpine-slim AS server

# Copy built files to the Nginx image
COPY --from=base /mzai/lumigator/frontend/dist /usr/share/nginx/html

# Copy a default nginx config, adjusted to support single page applications
COPY --from=base /mzai/lumigator/frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
