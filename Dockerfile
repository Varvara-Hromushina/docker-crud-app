# Stage 1: build
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY src ./src

RUN pip install --upgrade pip && \
    pip wheel . -w /wheels

# Stage 2.1: test 
FROM python:3.12-slim AS test

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY src ./src
COPY tests ./tests

RUN chmod -R a+r /app && \
    find /app -type d -exec chmod a+x {} \;

RUN pip install --no-cache-dir .[test]

ENV PYTHONPATH=/app:$PYTHONPATH

ENTRYPOINT ["sh", "-c"]
CMD ["pytest"]
# Stage 2.2: runtime
FROM python:3.12-slim

WORKDIR /app

COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*

COPY src ./src

CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port 8041"]
