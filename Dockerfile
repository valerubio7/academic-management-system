FROM python:3.12-slim-bullseye
 
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 


RUN apt-get update && \
    apt-get install -y --no-install-recommends postgresql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt  /app/
 
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media /app/logs

# Collect static files (will use WhiteNoise in production)
RUN python manage.py collectstatic --noinput || echo "Collectstatic skipped (no SECRET_KEY yet)"

EXPOSE 8000

# Use gunicorn for production (override with docker-compose for dev)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "config.wsgi:application"]