# Dockerfile for Django app with PostgreSQL
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt ./
RUN apt-get update && apt-get install -y --no-install-recommends netcat-openbsd \
	&& rm -rf /var/lib/apt/lists/* \
	&& pip install --upgrade pip && pip install -r requirements.txt

COPY . .
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Collect static files (if any)
RUN mkdir -p /app/static
RUN python manage.py collectstatic --noinput || true

ENTRYPOINT ["/entrypoint.sh"]
