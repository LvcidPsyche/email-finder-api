"""
Enhanced API documentation and metadata for OpenAPI/Swagger.
"""

API_DESCRIPTION = """
# Email Finder API

Find and verify professional email addresses using intelligent pattern matching and SMTP verification.

## Features

- **Pattern Generation**: 12+ common email patterns (first.last, firstlast, etc.)
- **MX Verification**: Check domain mail server configuration
- **SMTP Validation**: Verify if email mailbox actually exists
- **Catch-all Detection**: Identify domains that accept all emails
- **Bulk Operations**: Process up to 100 names at once
- **CSV Support**: Upload/download results in CSV format

## Authentication

All endpoints require an API key passed in the `X-API-Key` header:

```bash
curl -H "X-API-Key: your_api_key_here" https://api.example.com/api/find-email
```

## Rate Limits

| Plan | Requests/Day | Price |
|------|--------------|-------|
| Free | 10 | $0 |
| Starter | 500 | $49/mo |
| Pro | 5,000 | $99/mo |
| Enterprise | Unlimited | $199/mo |

Rate limit resets at midnight UTC.

## Error Codes

- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (invalid/missing API key)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

## Support

- Documentation: https://docs.example.com
- Email: support@example.com
- GitHub: https://github.com/yourusername/email-finder-api
"""

TAGS_METADATA = [
    {
        "name": "Authentication",
        "description": "User registration, login, and API key management",
    },
    {
        "name": "Email Finding",
        "description": "Find and generate email patterns for domains",
    },
    {
        "name": "Verification",
        "description": "Verify email deliverability and domain configuration",
    },
    {
        "name": "Bulk Operations",
        "description": "Process multiple emails or names at once",
    },
    {
        "name": "Utility",
        "description": "Health checks and system status",
    },
]

# Example responses for documentation
EXAMPLE_FIND_EMAIL_RESPONSE = {
    "success": True,
    "domain": "example.com",
    "person": {
        "first_name": "John",
        "last_name": "Doe"
    },
    "domain_accepts_email": True,
    "emails": [
        {
            "email": "john.doe@example.com",
            "pattern": "first.last",
            "confidence": 95
        },
        {
            "email": "johndoe@example.com",
            "pattern": "firstlast",
            "confidence": 85
        }
    ],
    "total_results": 12
}

EXAMPLE_VERIFY_EMAIL_RESPONSE = {
    "success": True,
    "email": "john.doe@example.com",
    "deliverable": True,
    "exists": True,
    "catch_all": False,
    "mx_host": "mail.example.com",
    "smtp_response": "250 OK"
}

EXAMPLE_ERROR_RESPONSE = {
    "detail": "Rate limit exceeded. Upgrade your plan for more requests."
}
