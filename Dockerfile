FROM python:3.14-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY tms_client.py .
COPY app.py .
COPY Procfile .

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os; import socket; s=socket.socket(); s.connect(('127.0.0.1', int(os.environ.get('PORT', 5000)))); s.close()" || exit 1

CMD gunicorn app:app --bind 0.0.0.0:$PORT
