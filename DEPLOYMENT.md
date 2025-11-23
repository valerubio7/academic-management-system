# Production Deployment Guide

## Academic Management System - Deployment Checklist

This document provides a comprehensive guide for deploying the Academic Management System to production.

## Table of Contents

1. [Pre-Deployment Requirements](#pre-deployment-requirements)
2. [Security Configuration](#security-configuration)
3. [Database Setup](#database-setup)
4. [Static Files and Media](#static-files-and-media)
5. [Deployment Steps](#deployment-steps)
6. [Post-Deployment Verification](#post-deployment-verification)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Requirements

### System Requirements

- **Server**: Linux-based OS (Ubuntu 22.04 LTS recommended)
- **RAM**: Minimum 2GB (4GB+ recommended)
- **Storage**: 20GB+ free space
- **CPU**: 2+ cores recommended
- **Network**: Static IP or domain name configured

### Software Requirements

- Docker Engine 24.0+
- Docker Compose 2.20+
- SSL/TLS certificates (Let's Encrypt recommended)
- Domain name with DNS configured

### Access Requirements

- SSH access to production server
- Sudo/root privileges
- Firewall configuration access
- Database backup location

---

## Security Configuration

### 1. Generate Strong Credentials

```bash
# Generate SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Generate strong database password (32 characters)
openssl rand -base64 32
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and update ALL values:

```bash
cp .env.example .env
chmod 600 .env  # Restrict permissions
```

**Critical variables to change:**

```env
SECRET_KEY=<YOUR_GENERATED_SECRET_KEY_HERE>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

POSTGRES_PASSWORD=<YOUR_STRONG_DB_PASSWORD>
EMAIL_HOST_PASSWORD=<YOUR_EMAIL_PASSWORD>

CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 3. Firewall Configuration

```bash
# Allow SSH (if not already allowed)
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Verify rules
sudo ufw status
```

### 4. SSL/TLS Certificate Setup

**Using Let's Encrypt (Certbot):**

```bash
# Install Certbot
sudo apt update
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Certificates will be in:
# /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

---

## Database Setup

### 1. Database Initialization

The database is automatically created by Docker Compose, but verify:

```bash
# Check database service
docker compose -f docker-compose.prod.yml ps db

# Verify database connection
docker compose -f docker-compose.prod.yml exec db psql -U ams_user -d academic_management_system -c "SELECT version();"
```

### 2. Apply Migrations

```bash
# Apply all migrations
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate

# Verify migrations
docker compose -f docker-compose.prod.yml exec backend python manage.py showmigrations
```

### 3. Database Backup Strategy

**Set up automated backups:**

Create `/opt/backups/db_backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CONTAINER_NAME="academic-management-system-db-1"
DB_NAME="academic_management_system"
DB_USER="ams_user"

mkdir -p $BACKUP_DIR

docker exec $CONTAINER_NAME pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/backup_$TIMESTAMP.sql.gz

# Keep only last 30 days of backups
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

echo "Backup completed: backup_$TIMESTAMP.sql.gz"
```

**Schedule with cron:**

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /opt/backups/db_backup.sh >> /var/log/db_backup.log 2>&1
```

---

## Static Files and Media

### 1. Collect Static Files

```bash
# Collect static files (WhiteNoise will serve them)
docker compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

### 2. Verify Static Files

Check that staticfiles directory is populated:

```bash
docker compose -f docker-compose.prod.yml exec backend ls -la staticfiles/
```

### 3. Media Files Storage

For production, consider using cloud storage (AWS S3, Google Cloud Storage):

**Optional: Configure S3 for media files**

Add to `requirements.txt`:

```
boto3==1.28.85
django-storages==1.14.2
```

Add to `config/settings.py`:

```python
if not DEBUG and os.getenv('AWS_STORAGE_BUCKET_NAME'):
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
```

---

## Deployment Steps

### Step-by-Step Production Deployment

**1. Clone repository on production server:**

```bash
cd /opt
sudo git clone <repository-url> academic-management-system
cd academic-management-system
sudo chown -R $USER:$USER .
```

**2. Configure environment:**

```bash
cp .env.example .env
nano .env  # Edit with production values
chmod 600 .env
```

**3. Build production image:**

```bash
docker compose -f docker-compose.prod.yml build --no-cache
```

**4. Start services:**

```bash
docker compose -f docker-compose.prod.yml up -d
```

**5. Verify services are running:**

```bash
docker compose -f docker-compose.prod.yml ps

# Should show:
# - db (healthy)
# - backend (healthy)
```

**6. Run migrations:**

```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate --noinput
```

**7. Collect static files:**

```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
```

**8. Create superuser:**

```bash
docker compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser
```

**9. Verify deployment:**

```bash
# Test health endpoint
curl http://localhost:8000/health/

# Expected output:
# {"status":"healthy","database":"connected"}
```

---

## Post-Deployment Verification

### 1. Functional Testing Checklist

- [ ] Home page loads correctly
- [ ] Login functionality works
- [ ] Static files (CSS/JS) load correctly
- [ ] Admin dashboard accessible
- [ ] Can create users (admin, professor, student)
- [ ] Can create faculties and careers
- [ ] Can create subjects
- [ ] Can enroll students in subjects
- [ ] Can create and assign grades
- [ ] Logout functionality works
- [ ] Error pages (404, 500) display correctly
- [ ] Health check endpoint responds

### 2. Security Verification

```bash
# Verify DEBUG is False
docker compose -f docker-compose.prod.yml exec backend python manage.py shell << EOF
from django.conf import settings
print(f"DEBUG: {settings.DEBUG}")
print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
print(f"SECRET_KEY length: {len(settings.SECRET_KEY)}")
EOF

# Expected output:
# DEBUG: False
# ALLOWED_HOSTS: ['yourdomain.com', 'www.yourdomain.com']
# SECRET_KEY length: 50+ characters
```

### 3. Performance Testing

```bash
# Test response time
time curl -I http://localhost:8000/

# Monitor resource usage
docker stats

# Check database connections
docker compose -f docker-compose.prod.yml exec db psql -U ams_user -d academic_management_system -c "SELECT count(*) FROM pg_stat_activity;"
```

---

## Monitoring and Maintenance

### 1. Log Monitoring

**View application logs:**

```bash
# Real-time logs
docker compose -f docker-compose.prod.yml logs -f backend

# Error logs only
docker compose -f docker-compose.prod.yml exec backend tail -f logs/django.log

# Last 100 lines
docker compose -f docker-compose.prod.yml logs --tail=100 backend
```

**Log rotation** is configured automatically (10MB files, 5 backups).

### 2. Health Monitoring

Set up external monitoring:

- **Uptime monitoring**: Use UptimeRobot, Pingdom, or StatusCake
- **Endpoint**: `https://yourdomain.com/health/`
- **Frequency**: Every 5 minutes
- **Alert on**: Non-200 response or response time > 5s

### 3. Resource Monitoring

```bash
# Container resource usage
docker stats

# Disk usage
df -h

# Database size
docker compose -f docker-compose.prod.yml exec db psql -U ams_user -d academic_management_system -c "SELECT pg_size_pretty(pg_database_size('academic_management_system'));"
```

### 4. Regular Maintenance Tasks

**Daily:**

- Monitor error logs
- Check health endpoint
- Verify backups completed

**Weekly:**

- Review access logs
- Check disk space
- Update packages in container (rebuild if needed)

**Monthly:**

- Review and optimize database queries
- Analyze slow logs
- Test disaster recovery procedure
- Security audit

---

## Troubleshooting

### Common Issues and Solutions

#### Application Won't Start

**Symptoms:** Container exits immediately

**Solutions:**

1. Check logs: `docker compose -f docker-compose.prod.yml logs backend`
2. Verify .env file exists and has correct values
3. Check SECRET_KEY is set
4. Verify ALLOWED_HOSTS is configured

```bash
# Validate environment
docker compose -f docker-compose.prod.yml exec backend python manage.py check --deploy
```

#### Database Connection Errors

**Symptoms:** "could not connect to server" errors

**Solutions:**

1. Verify database service is running:
   ```bash
   docker compose -f docker-compose.prod.yml ps db
   ```
2. Check database credentials in .env
3. Verify DATABASE_HOST=db (not localhost)
4. Check database logs:
   ```bash
   docker compose -f docker-compose.prod.yml logs db
   ```

#### Static Files Not Loading

**Symptoms:** 404 errors for CSS/JS, no styling

**Solutions:**

1. Run collectstatic:
   ```bash
   docker compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
   ```
2. Verify WhiteNoise in MIDDLEWARE (it is configured)
3. Check STATIC_ROOT and STATIC_URL settings
4. Clear browser cache

#### 500 Internal Server Error

**Symptoms:** Custom 500 page or generic error

**Solutions:**

1. Check error logs:
   ```bash
   docker compose -f docker-compose.prod.yml exec backend cat logs/django.log
   ```
2. Verify all migrations applied:
   ```bash
   docker compose -f docker-compose.prod.yml exec backend python manage.py migrate --check
   ```
3. Check DEBUG=False (must be False for custom error pages)
4. Verify templates exist (404.html, 500.html)

#### Performance Issues

**Symptoms:** Slow response times

**Solutions:**

1. Check resource usage: `docker stats`
2. Increase Gunicorn workers in Dockerfile
3. Enable Redis caching (uncomment in docker-compose.prod.yml)
4. Analyze slow queries:
   ```bash
   docker compose -f docker-compose.prod.yml exec db psql -U ams_user -d academic_management_system -c "SELECT query, calls, total_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
   ```
5. Add database indexes (already configured for main models)

#### Permission Errors

**Symptoms:** Permission denied errors in logs

**Solutions:**

```bash
# Fix ownership of volumes
docker compose -f docker-compose.prod.yml exec backend chown -R nobody:nogroup /app/media
docker compose -f docker-compose.prod.yml exec backend chown -R nobody:nogroup /app/logs
```

---

## Disaster Recovery

### Restore from Backup

**1. Stop services:**

```bash
docker compose -f docker-compose.prod.yml down
```

**2. Restore database:**

```bash
# Start only database
docker compose -f docker-compose.prod.yml up -d db

# Restore from backup
gunzip -c /opt/backups/postgres/backup_20250101_020000.sql.gz | \
  docker compose -f docker-compose.prod.yml exec -T db psql -U ams_user academic_management_system
```

**3. Start all services:**

```bash
docker compose -f docker-compose.prod.yml up -d
```

**4. Verify:**

```bash
curl http://localhost:8000/health/
```

---

## Performance Tuning

### Gunicorn Workers

Edit `Dockerfile` and adjust workers based on CPU cores:

```dockerfile
# Formula: workers = (2 * CPU_CORES) + 1
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "9", "--timeout", "120", "config.wsgi:application"]
```

### Enable Redis Caching

1. Uncomment Redis service in `docker-compose.prod.yml`
2. Set `REDIS_URL=redis://redis:6379/1` in `.env`
3. Restart services

### Database Optimization

```sql
-- Run VACUUM regularly
VACUUM ANALYZE;

-- Check for missing indexes
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats
WHERE schemaname = 'public'
ORDER BY abs(correlation) DESC;
```

---

## Security Hardening

### Additional Security Measures

1. **Enable fail2ban:**

   ```bash
   sudo apt install fail2ban
   sudo systemctl enable fail2ban
   ```

2. **Set up automatic security updates:**

   ```bash
   sudo apt install unattended-upgrades
   sudo dpkg-reconfigure -plow unattended-upgrades
   ```

3. **Disable password SSH (use keys only):**

   ```bash
   # Edit /etc/ssh/sshd_config
   PasswordAuthentication no
   sudo systemctl restart sshd
   ```

4. **Install and configure ModSecurity** (if using Nginx)

5. **Regular security audits:**
   ```bash
   # Check for vulnerable dependencies
   docker compose -f docker-compose.prod.yml exec backend pip list --outdated
   ```

---

## Support and Escalation

### Getting Help

1. Check logs first
2. Review this deployment guide
3. Consult main README.md
4. Check Django deployment checklist:
   ```bash
   docker compose -f docker-compose.prod.yml exec backend python manage.py check --deploy
   ```

### Emergency Contacts

- System Administrator: [contact info]
- Database Administrator: [contact info]
- Development Team: [contact info]

---

**Last Updated:** November 2025  
**Version:** 2.0.0
