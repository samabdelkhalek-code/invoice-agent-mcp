FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install "mcp[cli]>=1.0.0" httpx
COPY server.py .
EXPOSE 8090
ENV PORT=8090
CMD ["python3", "server.py", "sse"]
