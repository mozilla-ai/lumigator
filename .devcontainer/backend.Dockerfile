FROM python:3.10.13-bookworm

WORKDIR /app

COPY platform/python/mzai/backend .

CMD ["python3"]
