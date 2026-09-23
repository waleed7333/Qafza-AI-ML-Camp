FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    QAFZA_CONFIG=/app/config/settings.toml

WORKDIR /app

COPY requirements/runtime.txt /tmp/runtime.txt
RUN python -m pip install --upgrade pip \
    && python -m pip install -r /tmp/runtime.txt \
    && python -m pip check

COPY app ./app
COPY src ./src
COPY config ./config

RUN mkdir -p /app/logs

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
