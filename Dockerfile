FROM python:3.14-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY tms_client.py .
COPY app.py .

CMD exec gunicorn app:app --bind 0.0.0.0:${PORT:-5000} --workers 1 --timeout 120
