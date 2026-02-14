"""
Centralized error handling with enhanced error messages.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Base exception for API errors."""
    def __init__(self, status_code: int, message: str, details: dict = None):
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class RateLimitError(APIError):
    """Raised when rate limit is exceeded."""
    def __init__(self, plan_tier: str, limit: int, reset_time: str):
        super().__init__(
            status_code=429,
            message=f"Rate limit exceeded for {plan_tier} plan",
            details={
                "limit": limit,
                "reset_time": reset_time,
                "upgrade_url": "https://yourapi.com/pricing"
            }
        )


class InvalidAPIKeyError(APIError):
    """Raised when API key is invalid or missing."""
    def __init__(self):
        super().__init__(
            status_code=401,
            message="Invalid or missing API key",
            details={
                "help": "Get your API key at https://yourapi.com/dashboard",
                "header_format": "X-API-Key: your_api_key_here"
            }
        )


class ResourceNotFoundError(APIError):
    """Raised when requested resource doesn't exist."""
    def __init__(self, resource_type: str, identifier: str):
        super().__init__(
            status_code=404,
            message=f"{resource_type} not found",
            details={"identifier": identifier}
        )


async def api_error_handler(request: Request, exc: APIError):
    """Handle custom API errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.message,
            "details": exc.details,
            "path": str(request.url.path)
        }
    )


async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed messages."""
    errors = []
    for error in exc.errors():
        field = " -> ".join([str(loc) for loc in error["loc"]])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": "Validation error",
            "details": {
                "errors": errors,
                "help": "Check API documentation at /docs"
            },
            "path": str(request.url.path)
        }
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with enhanced messages."""
    # Map common status codes to helpful messages
    helpful_messages = {
        400: "Bad Request - Check your request parameters",
        401: "Unauthorized - Invalid or missing API key",
        403: "Forbidden - Insufficient permissions",
        404: "Not Found - Endpoint or resource doesn't exist",
        405: "Method Not Allowed - Check HTTP method (GET/POST/etc)",
        429: "Too Many Requests - Rate limit exceeded",
        500: "Internal Server Error - Please contact support",
        503: "Service Unavailable - Try again later"
    }
    
    message = helpful_messages.get(exc.status_code, exc.detail)
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": message,
            "details": {"original_error": str(exc.detail)} if exc.detail != message else {},
            "path": str(request.url.path)
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error on {request.url.path}: {str(exc)}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error",
            "details": {
                "message": "An unexpected error occurred",
                "support": "Contact support@yourapi.com with the request ID"
            },
            "path": str(request.url.path)
        }
    )


def register_error_handlers(app):
    """Register all error handlers with the FastAPI app."""
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
