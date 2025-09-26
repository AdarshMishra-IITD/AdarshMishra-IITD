# Dockerfile for Django app with PostgreSQL
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Collect static files (if any)
RUN mkdir -p /app/static
RUN python manage.py collectstatic --noinput || true

CMD ["gunicorn", "project_config.wsgi:application", "--bind", "0.0.0.0:8000"]
