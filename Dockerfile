FROM python:3.11-slim

# Non-root user for security
RUN useradd --create-home appuser

WORKDIR /app

# Install dependencies first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (no data, no models — see docs/DEPLOY.md)
COPY app/ app/
COPY web/ web/
COPY knowledge/ knowledge/
COPY config.py .
COPY .env.example .

# Models are NOT baked into the image (they exceed free-tier image limits).
# Provide them via a mounted volume or a download step in your run command.
# See docs/DEPLOY.md for details.
RUN mkdir -p models data/uploads

# Drop root
USER appuser

EXPOSE 8000

ENV ENV=prod
ENV PORT=8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/api/v1/health')"

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --workers 1
