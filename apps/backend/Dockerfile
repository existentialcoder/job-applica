FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# uid 1000 so files written to a bind-mounted uploads/ (APP_ENV=local) stay owned by the host user.
RUN useradd --uid 1000 --create-home app \
    && mkdir -p uploads/users && chown -R app:app uploads
USER app

EXPOSE 8000

CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
