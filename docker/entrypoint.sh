#!/bin/bash

echo "Waiting for postgres..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 1
done
echo "PostgreSQL started"

echo "Run migrations..."

alembic upgrade head

echo "End migrations..."

python -m src.manage create-superuser admin P@ssw0rd4312

gunicorn src.main:app --bind=0.0.0.0:8000  --workers 3 --worker-class uvicorn.workers.UvicornWorker