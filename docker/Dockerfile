# Build frontend
FROM node:22-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Production image
FROM python:3.13-slim
WORKDIR /app

COPY backend/pyproject.toml ./
RUN pip install --no-cache-dir .

COPY backend/ ./
COPY --from=frontend-build /app/frontend/dist /app/public

RUN mkdir -p /app/data /app/backups && \
    useradd -m appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8090

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8090"]
