#!/bin/sh
set -e

echo "==> Waiting for PostgreSQL to be ready..."
until python -c "import psycopg2; psycopg2.connect(host='${DATABASE_HOST}', port='${DATABASE_PORT}', user='${POSTGRES_USER}', password='${POSTGRES_PASSWORD}', dbname='${POSTGRES_DB}')" 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "==> PostgreSQL is up - continuing..."

echo "==> Running database migrations..."
python manage.py migrate --noinput

echo "==> Creating superuser if it doesn't exist..."
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: username=admin, password=admin123')
else:
    print('Superuser already exists')
EOF

echo "==> Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "==> Starting application..."
exec "$@"
