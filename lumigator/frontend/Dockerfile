ARG NODE_VERSION=18.20.0

FROM node:${NODE_VERSION}-alpine AS base

# Copy the project into the image
COPY ../../ /mzai

WORKDIR /mzai/

# Copy the .env file for the entire project, and perform some transformation on it.
# Only env vars starting with the 'VUE_APP_' prefix are made visible by the Vite build system (See: vite.config.js),
# but we extract only these variables in a kind of 'least privilege' way.
# See: https://cli.vuejs.org/guide/mode-and-env.html#environment-variables
COPY .env /mzai/lumigator/frontend/
RUN cat .env | grep -E ^VUE_APP_ > /mzai/lumigator/frontend/.env

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
