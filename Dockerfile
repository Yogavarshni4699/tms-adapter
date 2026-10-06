FROM python:3.14-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY tms_client.py .

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from tms_client import TMSClient; TMSClient().debug_echo()" || exit 1

CMD ["python", "-c", "from tms_client import TMSClient; print('TMS Adapter ready for use')"]
