FROM python:3.10.13-bookworm
WORKDIR /app
COPY platform.python.mzai.backend/backend_app.pex .
ENTRYPOINT ["./backend_app.pex"]