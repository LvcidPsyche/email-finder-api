#!/bin/bash
# cURL examples for Email Finder API

API_KEY="your_api_key_here"
BASE_URL="https://api.example.com"

echo "=== Email Finder API Examples ==="

# Register new user
echo -e "\n1. Register new user:"
curl -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'

# Login
echo -e "\n\n2. Login:"
curl -X POST "$BASE_URL/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'

# Find email
echo -e "\n\n3. Find email patterns:"
curl -X POST "$BASE_URL/api/find-email" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "first_name": "John",
    "last_name": "Doe"
  }'

# Verify email
echo -e "\n\n4. Verify email deliverability:"
curl -X POST "$BASE_URL/api/verify-email" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com"
  }'

# Verify domain
echo -e "\n\n5. Verify domain configuration:"
curl -X POST "$BASE_URL/api/verify-domain" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com"
  }'

# Bulk find
echo -e "\n\n6. Bulk find emails:"
curl -X POST "$BASE_URL/api/bulk-find" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "example.com",
    "names": [
      {"first_name": "John", "last_name": "Doe"},
      {"first_name": "Jane", "last_name": "Smith"}
    ]
  }'

# Check usage
echo -e "\n\n7. Check API usage:"
curl -X GET "$BASE_URL/api/usage" \
  -H "X-API-Key: $API_KEY"

# Health check
echo -e "\n\n8. Health check:"
curl -X GET "$BASE_URL/health"

echo -e "\n\nDone!"
