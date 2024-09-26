# Build library in a docker image, so we can pull it into other images

# TODO Make FROM an arg (Shared base image amongst all containers)
FROM python:3.11-slim-bookworm 
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy the project into the image
ADD . /app

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app

RUN uv sync --frozen

# Build dist and save it to image
RUN uv build