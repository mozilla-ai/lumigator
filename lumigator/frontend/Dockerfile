ARG NODE_VERSION=18.20.0

FROM node:${NODE_VERSION}-alpine AS base

# Copy the project into the image
COPY . /frontend

WORKDIR /frontend/

# Install dependencies
RUN npm install

# Build static files
RUN npm run build


FROM nginx:1.27.2-alpine-slim AS server

# Copy builded files to the Nginx image
COPY --from=base  /frontend/dist /usr/share/nginx/html

EXPOSE 80
