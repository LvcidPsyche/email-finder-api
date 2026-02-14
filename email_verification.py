"""
SMTP email verification and caching utilities.
"""
import smtplib
import dns.resolver
from typing import Optional
import time
import hashlib
import json
import os

# Simple in-memory cache for MX records (1 hour TTL)
_mx_cache = {}
MX_CACHE_TTL = 3600  # 1 hour in seconds


def get_mx_cache_key(domain: str) -> str:
    """Generate cache key for domain MX records."""
    return hashlib.md5(domain.lower().encode()).hexdigest()


def get_cached_mx(domain: str) -> Optional[dict]:
    """Get MX records from cache if not expired."""
    cache_key = get_mx_cache_key(domain)
    if cache_key in _mx_cache:
        cached_data, timestamp = _mx_cache[cache_key]
        if time.time() - timestamp < MX_CACHE_TTL:
            return cached_data
        else:
            # Expired, remove from cache
            del _mx_cache[cache_key]
    return None


def cache_mx_records(domain: str, mx_data: dict):
    """Cache MX records for a domain."""
    cache_key = get_mx_cache_key(domain)
    _mx_cache[cache_key] = (mx_data, time.time())


def check_mx_records_cached(domain: str) -> dict:
    """Check MX records with caching support."""
    # Try cache first
    cached = get_cached_mx(domain)
    if cached:
        return {**cached, "cached": True}

    # Not in cache, do DNS lookup
    try:
        answers = dns.resolver.resolve(domain, "MX")
        mx_records = []
        for rdata in answers:
            mx_records.append({
                "priority": rdata.preference,
                "host": str(rdata.exchange).rstrip("."),
            })
        mx_records.sort(key=lambda x: x["priority"])

        result = {
            "domain": domain,
            "has_mx": True,
            "accepts_email": True,
            "mx_records": mx_records,
            "record_count": len(mx_records),
            "cached": False
        }

        # Cache the result
        cache_mx_records(domain, result)
        return result

    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers) as e:
        result = {
            "domain": domain,
            "has_mx": False,
            "accepts_email": False,
            "mx_records": [],
            "record_count": 0,
            "error": str(type(e).__name__),
            "cached": False
        }
        return result
    except Exception as e:
        return {
            "domain": domain,
            "has_mx": False,
            "accepts_email": False,
            "mx_records": [],
            "record_count": 0,
            "error": str(e),
            "cached": False
        }


async def verify_email_smtp(email: str, timeout: int = 10) -> dict:
    """
    Verify an email address via SMTP.

    WARNING: This makes actual SMTP connections and may be blocked by some mail servers.
    Use sparingly and implement proper rate limiting.

    Returns:
        dict with keys: email, exists, deliverable, catch_all, mx_host, error
    """
    try:
        # Extract domain from email
        if "@" not in email:
            return {
                "email": email,
                "exists": False,
                "deliverable": False,
                "catch_all": False,
                "error": "Invalid email format"
            }

        domain = email.split("@")[1]

        # Get MX records
        mx_info = check_mx_records_cached(domain)
        if not mx_info["has_mx"]:
            return {
                "email": email,
                "exists": False,
                "deliverable": False,
                "catch_all": False,
                "error": "No MX records found"
            }

        # Get primary MX host
        mx_host = mx_info["mx_records"][0]["host"]

        # Try SMTP verification (simplified - real impl would need more checks)
        try:
            # Connect to SMTP server
            server = smtplib.SMTP(timeout=timeout)
            server.connect(mx_host)
            server.helo(server.local_hostname)

            # Try MAIL FROM
            code, message = server.mail('verify@example.com')
            if code != 250:
                server.quit()
                return {
                    "email": email,
                    "exists": False,
                    "deliverable": False,
                    "catch_all": False,
                    "mx_host": mx_host,
                    "error": f"MAIL FROM rejected: {code} {message.decode()}"
                }

            # Try RCPT TO
            code, message = server.rcpt(email)
            server.quit()

            if code == 250:
                return {
                    "email": email,
                    "exists": True,
                    "deliverable": True,
                    "catch_all": False,
                    "mx_host": mx_host
                }
            elif code == 550:
                return {
                    "email": email,
                    "exists": False,
                    "deliverable": False,
                    "catch_all": False,
                    "mx_host": mx_host,
                    "error": f"Mailbox does not exist: {message.decode()}"
                }
            else:
                return {
                    "email": email,
                    "exists": None,
                    "deliverable": False,
                    "catch_all": False,
                    "mx_host": mx_host,
                    "error": f"Unexpected SMTP code: {code} {message.decode()}"
                }

        except smtplib.SMTPException as e:
            return {
                "email": email,
                "exists": None,
                "deliverable": False,
                "catch_all": False,
                "mx_host": mx_host,
                "error": f"SMTP error: {str(e)}"
            }
        except Exception as e:
            return {
                "email": email,
                "exists": None,
                "deliverable": False,
                "catch_all": False,
                "mx_host": mx_host,
                "error": f"Connection error: {str(e)}"
            }

    except Exception as e:
        return {
            "email": email,
            "exists": None,
            "deliverable": False,
            "catch_all": False,
            "error": f"Verification failed: {str(e)}"
        }


def detect_catch_all(domain: str, timeout: int = 10) -> dict:
    """
    Detect if a domain uses catch-all email (accepts all addresses).

    Tests a random/invalid email to see if it's accepted.

    Returns:
        dict with keys: domain, is_catch_all, confidence, tested_email
    """
    import random
    import string

    # Generate random email
    random_local = ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))
    test_email = f"{random_local}@{domain}"

    # Get MX records
    mx_info = check_mx_records_cached(domain)
    if not mx_info["has_mx"]:
        return {
            "domain": domain,
            "is_catch_all": False,
            "confidence": 100,
            "error": "No MX records"
        }

    try:
        mx_host = mx_info["mx_records"][0]["host"]

        server = smtplib.SMTP(timeout=timeout)
        server.connect(mx_host)
        server.helo(server.local_hostname)
        server.mail('verify@example.com')

        code, message = server.rcpt(test_email)
        server.quit()

        if code == 250:
            return {
                "domain": domain,
                "is_catch_all": True,
                "confidence": 90,
                "tested_email": test_email,
                "mx_host": mx_host
            }
        else:
            return {
                "domain": domain,
                "is_catch_all": False,
                "confidence": 85,
                "tested_email": test_email,
                "mx_host": mx_host
            }

    except Exception as e:
        return {
            "domain": domain,
            "is_catch_all": None,
            "confidence": 0,
            "error": str(e)
        }


def get_domain_info(domain: str) -> dict:
    """
    Get enriched information about a domain.

    Returns company info, email provider detection, catch-all status.
    """
    mx_info = check_mx_records_cached(domain)

    # Detect email provider
    provider = "Unknown"
    if mx_info["has_mx"] and mx_info["mx_records"]:
        mx_host = mx_info["mx_records"][0]["host"].lower()
        if "google" in mx_host or "gmail" in mx_host:
            provider = "Google Workspace"
        elif "outlook" in mx_host or "microsoft" in mx_host or "office365" in mx_host:
            provider = "Microsoft 365"
        elif "protonmail" in mx_host:
            provider = "ProtonMail"
        elif "zoho" in mx_host:
            provider = "Zoho Mail"
        elif "mailgun" in mx_host:
            provider = "Mailgun"
        elif "sendgrid" in mx_host:
            provider = "SendGrid"

    # Check catch-all (optional, can be slow)
    # catch_all_info = detect_catch_all(domain)

    return {
        "domain": domain,
        "mx_info": mx_info,
        "email_provider": provider,
        "provider_detected": provider != "Unknown",
        # "catch_all": catch_all_info
    }
