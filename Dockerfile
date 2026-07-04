# syntax=docker/dockerfile:1
FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1 PYTHONPATH=/app/src
WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY pyproject.toml ./
COPY src ./src
COPY data ./data
RUN pip install -e .
# MCP servers speak over stdio; run the server as the container entrypoint.
ENTRYPOINT ["python", "-m", "mcprag.server"]
