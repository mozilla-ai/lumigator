FROM python:3.10.13-bookworm

WORKDIR /app

COPY platform/python/mzai/backend .
RUN mkdir /workspace

CMD ["/bin/sh", "-c", "echo Running\nwhile true; do sleep 1; done"]

