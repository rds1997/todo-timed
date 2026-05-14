FROM python:3.12-slim AS runtime
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app

# Stamped at build time and surfaced via GET /health so operators can confirm
# the running container is the freshly-built image (rules out stale layer cache).
ARG BUILD_ID=unset
ENV BUILD_ID=${BUILD_ID}

EXPOSE 8001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
