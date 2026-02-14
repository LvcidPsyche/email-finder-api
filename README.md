# Email Finder API

> Professional email discovery and verification service with pattern generation and MX validation

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

## Features

- 🔍 **Email Pattern Generation** - Generate 12+ common email patterns for any name + domain
- ✅ **MX Record Verification** - Verify domain accepts email with DNS lookup
- 📊 **Bulk Processing** - Process up to 100 names per request
- 🔐 **Secure Authentication** - JWT-based user auth + API key management
- 📈 **Usage Tracking** - Built-in rate limiting and usage analytics
- 🚀 **Fast & Reliable** - Built on FastAPI with async support

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/LvcidPsyche/email-finder-api.git
cd email-finder-api

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env with your configuration

# Run the server
python main.py
```

Server will start on `http://localhost:8770`

### Demo

Try the live demo at the web interface or use the API with the demo key:

```bash
curl -X POST http://localhost:8770/api/find-email \
  -H "Content-Type: application/json" \
  -H "X-API-Key: demo-key-2024" \
  -d '{
    "domain": "company.com",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

## API Documentation

### Authentication

All API endpoints require an API key passed in the `X-API-Key` header.

**Free demo key:** `demo-key-2024` (10 requests/day)

### Endpoints

#### POST `/api/auth/register`

Register a new user and get an API key.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Registration successful",
  "token": "eyJ0eXAiOiJKV1QiLCJhbG...",
  "api_key": "a1b2c3d4-e5f6g7h8i9j0k1l2m3n4o5p6",
  "plan": "free"
}
```

#### POST `/api/auth/login`

Login with email and password to get JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

#### GET `/api/usage`

Get current usage statistics.

**Headers:** `X-API-Key: your-api-key`

**Response:**
```json
{
  "success": true,
  "total_calls": 45,
  "plan_tier": "free",
  "rate_limit": 500,
  "remaining": 455,
  "period_days": 1
}
```

#### POST `/api/find-email`

Find email patterns for a person at a domain.

**Headers:** `X-API-Key: your-api-key`

**Request:**
```json
{
  "domain": "company.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**
```json
{
  "success": true,
  "domain": "company.com",
  "person": {
    "first_name": "John",
    "last_name": "Doe"
  },
  "domain_accepts_email": true,
  "emails": [
    {
      "email": "john.doe@company.com",
      "pattern": "first.last",
      "confidence": 95
    },
    {
      "email": "johndoe@company.com",
      "pattern": "firstlast",
      "confidence": 85
    }
    // ... more patterns
  ],
  "total_results": 12
}
```

#### POST `/api/verify-domain`

Check if a domain accepts email (MX records).

**Request:**
```json
{
  "domain": "company.com"
}
```

**Response:**
```json
{
  "success": true,
  "domain": "company.com",
  "has_mx": true,
  "accepts_email": true,
  "mx_records": [
    {
      "priority": 10,
      "host": "mail.company.com"
    }
  ],
  "record_count": 1
}
```

#### POST `/api/bulk-find`

Find emails for multiple people at once (max 100).

**Request:**
```json
{
  "domain": "company.com",
  "names": [
    {"first_name": "John", "last_name": "Doe"},
    {"first_name": "Jane", "last_name": "Smith"}
  ]
}
```

#### GET `/api/patterns/{domain}`

Get common email patterns used by a domain.

**Response:**
```json
{
  "success": true,
  "domain": "company.com",
  "domain_accepts_email": true,
  "patterns": [
    {
      "pattern": "first.last",
      "example": "john.doe@company.com",
      "commonality": "Very Common"
    }
    // ... more patterns
  ],
  "total_patterns": 10
}
```

## Rate Limits

| Plan | Daily Limit | Price |
|------|-------------|-------|
| Free (Demo) | 10 requests | Free |
| Starter | 500 requests | $49/month |
| Pro | 5,000 requests | $99/month |
| Enterprise | Unlimited | $199/month |

Rate limit headers are included in all responses:
- `X-RateLimit-Limit` - Your plan's daily limit
- `X-RateLimit-Remaining` - Requests remaining today
- `X-RateLimit-Reset` - Seconds until limit resets

## Environment Variables

Create a `.env` file with these variables:

```bash
# Server Configuration
PORT=8770
HOST=0.0.0.0

# Security
API_KEY_SECRET=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# Database
DATABASE_URL=sqlite:///./data.db

# CORS
CORS_ORIGINS=*

# Rate Limiting
RATE_LIMIT_FREE=10
RATE_LIMIT_STARTER=500
RATE_LIMIT_PRO=5000
RATE_LIMIT_ENTERPRISE=999999

# Logging
LOG_LEVEL=INFO
```

## Development

### Project Structure

```
email-finder-api/
├── main.py              # FastAPI application
├── database.py          # Database models and auth
├── auth.py              # Authentication middleware
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
├── static/              # Static assets (CSS, JS)
├── templates/           # HTML templates
│   └── index.html      # Landing page
└── data.db             # SQLite database (generated)
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### Docker Deployment

```bash
# Build image
docker build -t email-finder-api .

# Run container
docker run -p 8770:8770 --env-file .env email-finder-api
```

## Technologies Used

- **FastAPI** - Modern, fast web framework
- **dnspython** - DNS resolver for MX record validation
- **aiosqlite** - Async SQLite database
- **PyJWT** - JSON Web Token authentication
- **passlib** - Password hashing
- **slowapi** - Rate limiting
- **uvicorn** - ASGI server

## License

MIT License - see LICENSE file for details

## Support

- Documentation: `/docs` endpoint (Swagger UI)
- Issues: [GitHub Issues](https://github.com/LvcidPsyche/email-finder-api/issues)
- Email: support@example.com

## Roadmap

- [ ] SMTP verification (actual mailbox checking)
- [ ] CSV import/export
- [ ] Webhook callbacks for bulk operations
- [ ] Domain enrichment (company info)
- [ ] Catch-all detection
- [ ] API client libraries (Python, JavaScript, PHP)

---

**Built with ❤️ by LvcidPsyche**
