FROM python:3.10 as builder
WORKDIR /app
COPY pyproject.toml .
RUN pip install --user ".[test]"

FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY src/ ./src/
COPY tests/ ./tests/
ENV PATH=/root/.local/bin:$PATH
ENTRYPOINT ["uvicorn"]
CMD ["src.main:app", "--host", "0.0.0.0", "--port", "8108"]
