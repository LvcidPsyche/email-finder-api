"""
Authentication and rate limiting middleware.
"""
from fastapi import Header, HTTPException, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
from typing import Optional
import database

# Rate limiter
limiter = Limiter(key_func=get_remote_address)


async def verify_api_key_dependency(x_api_key: str = Header(...)) -> dict:
    """Dependency to verify API key and return key info."""
    key_info = await database.verify_api_key(x_api_key)
    if not key_info:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return key_info


async def log_request_middleware(request: Request, call_next):
    """Middleware to log API requests and track usage."""
    start_time = time.time()

    # Extract API key from headers
    api_key = request.headers.get("x-api-key")

    response = await call_next(request)

    # Calculate response time
    response_time_ms = int((time.time() - start_time) * 1000)

    # Log usage if API key is present and valid
    if api_key:
        key_info = await database.verify_api_key(api_key)
        if key_info:
            await database.log_usage(
                api_key_id=key_info["api_key_id"],
                endpoint=request.url.path,
                response_time_ms=response_time_ms,
                status_code=response.status_code
            )

    # Add custom headers
    response.headers["X-Response-Time"] = f"{response_time_ms}ms"

    return response


async def rate_limit_middleware(request: Request, call_next):
    """Check rate limits before processing request."""
    # Skip rate limiting for non-API routes
    if not request.url.path.startswith("/api/"):
        return await call_next(request)

    # Skip for health check
    if request.url.path == "/health":
        return await call_next(request)

    # Extract API key
    api_key = request.headers.get("x-api-key")
    if not api_key:
        return await call_next(request)  # Let endpoint handle missing key

    # Verify key and check limits
    key_info = await database.verify_api_key(api_key)
    if not key_info:
        return await call_next(request)  # Let endpoint handle invalid key

    # Get usage stats (check daily usage)
    stats = await database.get_usage_stats(key_info["api_key_id"], days=1)

    if stats["remaining"] <= 0:
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "plan": stats["plan_tier"],
                "limit": stats["rate_limit"],
                "used": stats["total_calls"],
                "resets_in": "24 hours"
            },
            headers={
                "X-RateLimit-Limit": str(stats["rate_limit"]),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": "86400"
            }
        )

    # Add rate limit headers
    response = await call_next(request)
    response.headers["X-RateLimit-Limit"] = str(stats["rate_limit"])
    response.headers["X-RateLimit-Remaining"] = str(stats["remaining"])
    response.headers["X-RateLimit-Reset"] = "86400"  # 24 hours in seconds

    return response


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Handler for rate limit exceeded errors."""
    return JSONResponse(
        status_code=429,
        content={
            "error": "Too many requests",
            "detail": "Rate limit exceeded. Please try again later."
        }
    )
