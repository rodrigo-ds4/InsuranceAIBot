FROM python:3.12-slim AS server

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Build the policy index before serving (vector DB is separate from serving).
RUN mkdir -p data/chroma && python -m src.ingest || true

EXPOSE 5000

CMD ["python", "app.py"]