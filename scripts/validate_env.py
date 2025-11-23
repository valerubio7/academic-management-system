#!/usr/bin/env python
"""
Environment Validation Script for Production Deployment

This script validates that all required environment variables are set
and that their values are appropriate for production deployment.

Usage:
    python scripts/validate_env.py

Exit codes:
    0 - All checks passed
    1 - Validation failed
"""

import os
import sys
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Load environment variables
from dotenv import load_dotenv

load_dotenv()


class Colors:
    """ANSI color codes for terminal output."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"


def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}\n")


def print_success(text):
    """Print a success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text):
    """Print an error message."""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_warning(text):
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def check_required_var(name, min_length=1, description=""):
    """
    Check if a required environment variable is set and valid.

    Args:
        name: Variable name
        min_length: Minimum required length
        description: Human-readable description

    Returns:
        bool: True if valid, False otherwise
    """
    value = os.getenv(name)

    if not value:
        print_error(f"{name} is not set")
        if description:
            print(f"  {description}")
        return False

    if len(value) < min_length:
        print_error(f"{name} is too short (minimum {min_length} characters)")
        return False

    if value in ["change-me", "changeme", "password", "secret", "example"]:
        print_error(f"{name} contains a default/example value")
        return False

    print_success(f"{name} is set ({len(value)} characters)")
    return True


def check_secret_key():
    """Validate SECRET_KEY."""
    secret_key = os.getenv("SECRET_KEY")

    if not secret_key:
        print_error("SECRET_KEY is not set")
        print(
            '  Generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"'
        )
        return False

    if len(secret_key) < 50:
        print_error(f"SECRET_KEY is too short ({len(secret_key)} chars, minimum 50)")
        return False

    if secret_key == "insecure-default-key":
        print_error("SECRET_KEY is using the insecure default value")
        return False

    if "change" in secret_key.lower():
        print_warning("SECRET_KEY might contain placeholder text")
        return False

    print_success(f"SECRET_KEY is set ({len(secret_key)} characters)")
    return True


def check_debug_mode():
    """Validate DEBUG setting."""
    debug = os.getenv("DEBUG", "False").lower()

    if debug in ["true", "1", "yes"]:
        print_error("DEBUG is set to True - NEVER use in production!")
        return False

    print_success("DEBUG is set to False (production mode)")
    return True


def check_allowed_hosts():
    """Validate ALLOWED_HOSTS."""
    allowed_hosts = os.getenv("ALLOWED_HOSTS", "")

    if not allowed_hosts:
        print_error("ALLOWED_HOSTS is not set")
        return False

    hosts = [h.strip() for h in allowed_hosts.split(",") if h.strip()]

    if not hosts:
        print_error("ALLOWED_HOSTS is empty")
        return False

    # Check for common issues
    issues = []
    for host in hosts:
        if host in ["0.0.0.0", "*"]:
            issues.append(f"Insecure host: {host}")
        if host in ["localhost", "127.0.0.1"] and len(hosts) == 1:
            issues.append("Only localhost configured - add production domain")

    if issues:
        for issue in issues:
            print_warning(issue)

    print_success(f"ALLOWED_HOSTS configured: {', '.join(hosts)}")
    return True


def check_database_config():
    """Validate database configuration."""
    checks = [
        ("POSTGRES_DB", 3, "Database name"),
        ("POSTGRES_USER", 3, "Database user"),
        ("POSTGRES_PASSWORD", 16, "Database password (minimum 16 chars for security)"),
    ]

    all_valid = True
    for var, min_len, desc in checks:
        if not check_required_var(var, min_len, desc):
            all_valid = False

    # Check database password strength
    db_pass = os.getenv("POSTGRES_PASSWORD", "")
    if db_pass and len(db_pass) < 16:
        print_warning("Database password is weak (< 16 characters)")

    return all_valid


def check_email_config():
    """Check email configuration (optional but recommended)."""
    email_backend = os.getenv("EMAIL_BACKEND", "")

    if not email_backend:
        print_warning("EMAIL_BACKEND not configured - password resets won't work")
        return True  # Optional, so don't fail

    if "smtp" in email_backend.lower():
        # SMTP backend requires additional settings
        required = ["EMAIL_HOST", "EMAIL_HOST_USER", "EMAIL_HOST_PASSWORD"]
        missing = [var for var in required if not os.getenv(var)]

        if missing:
            print_warning(f"SMTP backend configured but missing: {', '.join(missing)}")
            return True

        print_success("Email configuration appears complete")

    return True


def check_csrf_origins():
    """Check CSRF trusted origins for HTTPS."""
    origins = os.getenv("CSRF_TRUSTED_ORIGINS", "")

    if not origins:
        print_warning("CSRF_TRUSTED_ORIGINS not set - required for HTTPS in production")
        print("  Example: https://yourdomain.com,https://www.yourdomain.com")
        return True  # Don't fail, but warn

    origin_list = [o.strip() for o in origins.split(",") if o.strip()]

    # Check that all origins use HTTPS
    for origin in origin_list:
        if not origin.startswith("https://"):
            print_warning(f"CSRF origin not using HTTPS: {origin}")

    print_success(f"CSRF_TRUSTED_ORIGINS configured: {len(origin_list)} origins")
    return True


def check_file_permissions():
    """Check that .env file has appropriate permissions."""
    env_file = BASE_DIR / ".env"

    if not env_file.exists():
        print_error(".env file not found")
        print("  Copy .env.example to .env and configure it")
        return False

    # Check permissions (Unix/Linux only)
    if hasattr(os, "stat"):
        import stat

        mode = os.stat(env_file).st_mode
        # Check if file is readable by others (should not be)
        if mode & stat.S_IROTH:
            print_warning(".env file is readable by others")
            print("  Run: chmod 600 .env")

    print_success(".env file exists")
    return True


def main():
    """Run all validation checks."""
    print_header("Production Environment Validation")

    print(f"{Colors.BOLD}Checking environment configuration...{Colors.END}\n")

    checks = [
        ("File Permissions", check_file_permissions),
        ("SECRET_KEY", check_secret_key),
        ("DEBUG Mode", check_debug_mode),
        ("ALLOWED_HOSTS", check_allowed_hosts),
        ("Database Configuration", check_database_config),
        ("Email Configuration", check_email_config),
        ("CSRF Origins", check_csrf_origins),
    ]

    results = []
    for name, check_func in checks:
        print(f"\n{Colors.BOLD}Checking {name}:{Colors.END}")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Error during check: {e}")
            results.append((name, False))

    # Summary
    print_header("Validation Summary")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        if result:
            print_success(f"{name}: PASSED")
        else:
            print_error(f"{name}: FAILED")

    print(f"\n{Colors.BOLD}Results: {passed}/{total} checks passed{Colors.END}\n")

    if passed == total:
        print_success("All validation checks passed!")
        print(
            f"\n{Colors.GREEN}Environment is ready for production deployment.{Colors.END}\n"
        )
        return 0
    else:
        print_error(f"{total - passed} validation check(s) failed")
        print(
            f"\n{Colors.RED}Fix the issues above before deploying to production.{Colors.END}\n"
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
