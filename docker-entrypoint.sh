#!/bin/sh

# Resolve database connection variables.
# Priority: DATABASE_URL (Railway standard) > PG* vars (Railway legacy) > POSTGRES_* / DATABASE_* (Docker Compose)
if [ -n "$DATABASE_URL" ]; then
  echo "==> Using DATABASE_URL for database connection"
else
  DB_HOST="${PGHOST:-${DATABASE_HOST:-localhost}}"
  DB_PORT="${PGPORT:-${DATABASE_PORT:-5432}}"
  DB_USER="${PGUSER:-${POSTGRES_USER}}"
  DB_NAME="${PGDATABASE:-${POSTGRES_DB}}"
  echo "==> Database config: host=${DB_HOST} port=${DB_PORT} user=${DB_USER} dbname=${DB_NAME}"
fi

# --- Best-effort database setup ---
# These steps are NOT fatal. If the DB is unavailable, Gunicorn still starts
# so Railway's healthcheck can reach /health/ and the deploy succeeds.
# The app will return 500s on DB-dependent pages until the DB is ready.

echo "==> Waiting for PostgreSQL to be ready..."
RETRIES=0
MAX_RETRIES=15
DB_READY=false
until python -c "
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection
connection.ensure_connection()
" 2>&1; do
  RETRIES=$((RETRIES + 1))
  if [ "$RETRIES" -ge "$MAX_RETRIES" ]; then
    echo "==> WARNING: Could not connect to PostgreSQL after ${MAX_RETRIES} attempts. Starting without DB."
    break
  fi
  echo "PostgreSQL is unavailable (attempt ${RETRIES}/${MAX_RETRIES}) - sleeping 2s"
  sleep 2
done

if [ "$RETRIES" -lt "$MAX_RETRIES" ]; then
  DB_READY=true
  echo "==> PostgreSQL is up - continuing..."
fi

if [ "$DB_READY" = true ]; then
  echo "==> Running database migrations..."
  python manage.py migrate --noinput || echo "==> WARNING: Migrations failed (will retry on next deploy)"

  echo "==> Creating superuser if it doesn't exist..."
  python manage.py shell <<EOF || echo "==> WARNING: Superuser creation failed"
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: username=admin, password=admin123')
else:
    print('Superuser already exists')
EOF

  echo "==> Seeding database with demo data..."
  python manage.py seed_data || echo "==> WARNING: Seed data failed"
else
  echo "==> Skipping migrations and superuser creation (DB not available)"
fi

echo "==> Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "==> Starting application..."
exec "$@"
