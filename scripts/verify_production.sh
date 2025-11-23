#!/bin/bash
#
# Quick Production Verification Script
# 
# This script performs basic checks to verify the production environment
# is properly configured before deployment.
#
# Usage:
#   ./scripts/verify_production.sh
#

set -e

echo "=========================================="
echo "  Production Verification Checklist"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check functions
check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    FAILED=1
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

FAILED=0

# 1. Check .env file exists
echo "Checking environment configuration..."
if [ -f .env ]; then
    check_pass ".env file exists"
    
    # Check .env permissions
    if [ "$(stat -c %a .env 2>/dev/null || stat -f %A .env 2>/dev/null)" = "600" ]; then
        check_pass ".env has secure permissions (600)"
    else
        check_warn ".env permissions should be 600 (run: chmod 600 .env)"
    fi
else
    check_fail ".env file not found (copy from .env.example)"
fi

# 2. Check Python dependencies
echo ""
echo "Checking dependencies..."
if [ -f requirements.txt ]; then
    check_pass "requirements.txt exists"
else
    check_fail "requirements.txt not found"
fi

# 3. Check Docker
echo ""
echo "Checking Docker..."
if command -v docker &> /dev/null; then
    check_pass "Docker is installed"
    
    if docker compose version &> /dev/null; then
        check_pass "Docker Compose is installed"
    else
        check_fail "Docker Compose is not installed"
    fi
else
    check_fail "Docker is not installed"
fi

# 4. Check critical files
echo ""
echo "Checking critical files..."
CRITICAL_FILES=(
    "config/settings.py"
    "config/health_check.py"
    "Dockerfile"
    "docker-compose.prod.yml"
    "Makefile"
    "templates/404.html"
    "templates/500.html"
    "app/migrations/0003_add_database_indexes.py"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        check_pass "$file exists"
    else
        check_fail "$file not found"
    fi
done

# 5. Check migrations are tracked
echo ""
echo "Checking migrations..."
if git check-ignore app/migrations/*.py &>/dev/null; then
    check_fail "Migrations are being ignored by git!"
else
    check_pass "Migrations are tracked by git"
fi

# 6. Validate environment variables
echo ""
echo "Validating environment variables..."
if [ -f scripts/validate_env.py ]; then
    if python scripts/validate_env.py; then
        check_pass "Environment validation passed"
    else
        check_fail "Environment validation failed"
    fi
else
    check_warn "Environment validation script not found"
fi

# 7. Check documentation
echo ""
echo "Checking documentation..."
DOC_FILES=("README.md" "DEPLOYMENT.md" ".env.example")
for file in "${DOC_FILES[@]}"; do
    if [ -f "$file" ]; then
        check_pass "$file exists"
    else
        check_warn "$file not found"
    fi
done

# Summary
echo ""
echo "=========================================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Review and update .env with production values"
    echo "  2. Generate a strong SECRET_KEY"
    echo "  3. Set DEBUG=False"
    echo "  4. Configure ALLOWED_HOSTS with your domain"
    echo "  5. Run: make deploy-prod"
    echo ""
    exit 0
else
    echo -e "${RED}Some checks failed!${NC}"
    echo ""
    echo "Please fix the issues above before deploying to production."
    echo "See DEPLOYMENT.md for detailed instructions."
    echo ""
    exit 1
fi
