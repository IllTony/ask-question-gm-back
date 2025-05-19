# Стадия сборки
FROM python:3.11.9-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN adduser appuser
WORKDIR /app

COPY ./requirements.txt ./

RUN apt-get update \
    && apt-get install -y libpq-dev gcc \
    && apt install -y netcat-traditional \
    && rm -rf /var/lib/apt/lists/*  \
    && pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org --upgrade --no-cache-dir pip \
    && pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org --no-cache-dir --no-deps -r requirements.txt

# Копируем код приложения
COPY --chown=appuser:appuser ./src/ ./src
COPY --chown=appuser:appuser ./migrations/ ./migrations
COPY --chown=appuser:appuser ./alembic.ini ./
COPY --chown=appuser:appuser ./docker/entrypoint.sh ./

RUN sed -i 's/\r$//g' entrypoint.sh \
  && chmod +x entrypoint.sh

USER appuser

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]