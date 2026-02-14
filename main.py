import dns.resolver
from fastapi import FastAPI, Request, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
from typing import Optional
from dotenv import load_dotenv
import uvicorn
import os
import time
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

# Import our auth and database modules
import database
import auth

# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize database
    await database.init_database()
    print("✓ Database initialized")
    yield
    # Shutdown: cleanup if needed
    print("✓ Shutting down")

app = FastAPI(
    title="Email Finder API",
    version="2.0.0",
    description="Find and verify professional email addresses",
    lifespan=lifespan
)

# CORS middleware
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.middleware("http")(auth.rate_limit_middleware)
app.middleware("http")(auth.log_request_middleware)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# --- Models ---

class FindEmailRequest(BaseModel):
    domain: str
    first_name: str
    last_name: str


class VerifyDomainRequest(BaseModel):
    domain: str


class NameEntry(BaseModel):
    first_name: str
    last_name: str


class BulkFindRequest(BaseModel):
    domain: str
    names: list[NameEntry]


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# --- Helper functions ---

def generate_email_patterns(first_name: str, last_name: str, domain: str) -> list[dict]:
    """Generate common email patterns for a given name and domain."""
    first = first_name.lower().strip()
    last = last_name.lower().strip()
    f_initial = first[0] if first else ""
    l_initial = last[0] if last else ""

    patterns = [
        {"email": f"{first}.{last}@{domain}", "pattern": "first.last", "confidence": 95},
        {"email": f"{first}{last}@{domain}", "pattern": "firstlast", "confidence": 85},
        {"email": f"{first}@{domain}", "pattern": "first", "confidence": 70},
        {"email": f"{f_initial}{last}@{domain}", "pattern": "flast", "confidence": 80},
        {"email": f"{first}{l_initial}@{domain}", "pattern": "firstl", "confidence": 65},
        {"email": f"{first}_{last}@{domain}", "pattern": "first_last", "confidence": 75},
        {"email": f"{first}-{last}@{domain}", "pattern": "first-last", "confidence": 70},
        {"email": f"{last}.{first}@{domain}", "pattern": "last.first", "confidence": 60},
        {"email": f"{last}{first}@{domain}", "pattern": "lastfirst", "confidence": 55},
        {"email": f"{f_initial}.{last}@{domain}", "pattern": "f.last", "confidence": 78},
        {"email": f"{last}@{domain}", "pattern": "last", "confidence": 50},
        {"email": f"{f_initial}{l_initial}@{domain}", "pattern": "fl", "confidence": 30},
    ]

    return patterns


def get_domain_patterns(domain: str) -> list[dict]:
    """Return common email patterns for a given domain."""
    return [
        {"pattern": "first.last", "example": f"john.doe@{domain}", "commonality": "Very Common"},
        {"pattern": "firstlast", "example": f"johndoe@{domain}", "commonality": "Common"},
        {"pattern": "first", "example": f"john@{domain}", "commonality": "Common"},
        {"pattern": "flast", "example": f"jdoe@{domain}", "commonality": "Common"},
        {"pattern": "first_last", "example": f"john_doe@{domain}", "commonality": "Moderate"},
        {"pattern": "first-last", "example": f"john-doe@{domain}", "commonality": "Moderate"},
        {"pattern": "f.last", "example": f"j.doe@{domain}", "commonality": "Moderate"},
        {"pattern": "last.first", "example": f"doe.john@{domain}", "commonality": "Less Common"},
        {"pattern": "firstl", "example": f"johnd@{domain}", "commonality": "Less Common"},
        {"pattern": "last", "example": f"doe@{domain}", "commonality": "Less Common"},
    ]


def check_mx_records(domain: str) -> dict:
    """Check MX records for a domain (with caching via email_verification module)."""
    return check_mx_records_cached(domain)


# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "2.0.0",
        "timestamp": int(time.time())
    }


# --- Auth endpoints ---

@app.post("/api/auth/register")
async def register(body: RegisterRequest):
    """Register a new user."""
    user_id = await database.create_user(body.email, body.password)
    if not user_id:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Auto-create a free tier API key
    api_key = await database.create_api_key_for_user(user_id, plan_tier="free")

    # Create JWT token
    token = database.create_jwt_token(user_id, body.email)

    return {
        "success": True,
        "message": "Registration successful",
        "token": token,
        "api_key": api_key,
        "plan": "free"
    }


@app.post("/api/auth/login")
async def login(body: LoginRequest):
    """Login and get JWT token."""
    user = await database.authenticate_user(body.email, body.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = database.create_jwt_token(user["id"], user["email"])

    return {
        "success": True,
        "token": token,
        "user": {
            "id": user["id"],
            "email": user["email"]
        }
    }


@app.get("/api/usage")
async def get_usage(key_info: dict = Depends(auth.verify_api_key_dependency)):
    """Get usage statistics for the current API key."""
    stats = await database.get_usage_stats(key_info["api_key_id"], days=1)
    return {
        "success": True,
        **stats
    }


# --- Email finding endpoints ---

@app.post("/api/find-email")
async def find_email(body: FindEmailRequest, key_info: dict = Depends(auth.verify_api_key_dependency)):
    domain = body.domain.lower().strip()
    first_name = body.first_name.strip()
    last_name = body.last_name.strip()

    if not domain or not first_name or not last_name:
        raise HTTPException(status_code=400, detail="domain, first_name, and last_name are required")

    patterns = generate_email_patterns(first_name, last_name, domain)
    mx_info = check_mx_records(domain)

    return {
        "success": True,
        "domain": domain,
        "person": {"first_name": first_name, "last_name": last_name},
        "domain_accepts_email": mx_info["accepts_email"],
        "emails": patterns,
        "total_results": len(patterns),
    }


@app.post("/api/verify-domain")
async def verify_domain(body: VerifyDomainRequest, key_info: dict = Depends(auth.verify_api_key_dependency)):
    domain = body.domain.lower().strip()
    if not domain:
        raise HTTPException(status_code=400, detail="domain is required")

    result = check_mx_records(domain)
    return {"success": True, **result}


@app.post("/api/bulk-find")
async def bulk_find(body: BulkFindRequest, key_info: dict = Depends(auth.verify_api_key_dependency)):
    domain = body.domain.lower().strip()
    names = body.names

    if not domain:
        raise HTTPException(status_code=400, detail="domain is required")
    if not names or len(names) == 0:
        raise HTTPException(status_code=400, detail="names list is required and must not be empty")
    if len(names) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 names per bulk request")

    mx_info = check_mx_records(domain)
    results = []
    for entry in names:
        patterns = generate_email_patterns(entry.first_name, entry.last_name, domain)
        results.append({
            "person": {"first_name": entry.first_name, "last_name": entry.last_name},
            "emails": patterns,
            "total_results": len(patterns),
        })

    return {
        "success": True,
        "domain": domain,
        "domain_accepts_email": mx_info["accepts_email"],
        "results": results,
        "total_people": len(results),
    }


@app.get("/api/patterns/{domain}")
async def get_patterns(domain: str, key_info: dict = Depends(auth.verify_api_key_dependency)):
    domain = domain.lower().strip()
    if not domain:
        raise HTTPException(status_code=400, detail="domain is required")

    patterns = get_domain_patterns(domain)
    mx_info = check_mx_records(domain)

    return {
        "success": True,
        "domain": domain,
        "domain_accepts_email": mx_info["accepts_email"],
        "patterns": patterns,
        "total_patterns": len(patterns),
    }


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8770"))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run("main:app", host=host, port=port, reload=True)

# --- Enhanced endpoints (Phase 2) ---

from email_verification import verify_email_smtp, check_mx_records_cached, get_domain_info, detect_catch_all
from csv_handler import parse_csv_upload, export_results_to_csv, export_verification_results_to_csv
from fastapi import UploadFile, File, BackgroundTasks
from fastapi.responses import StreamingResponse
import io


class VerifyEmailRequest(BaseModel):
    email: str


class BulkVerifyRequest(BaseModel):
    emails: list[str]


class DomainInfoRequest(BaseModel):
    domain: str


@app.post("/api/verify-email")
async def verify_single_email(body: VerifyEmailRequest, key_info: dict = Depends(auth.verify_api_key_dependency)):
    """Verify a single email address via SMTP (checks if mailbox exists)."""
    result = await verify_email_smtp(body.email)
    return {
        "success": True,
        **result
    }


@app.post("/api/bulk-verify")
async def bulk_verify_emails(body: BulkVerifyRequest, key_info: dict = Depends(auth.verify_api_key_dependency)):
    """Verify multiple email addresses (max 50 per request)."""
    if len(body.emails) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 emails per request")
    
    results = []
    for email in body.emails:
        result = await verify_email_smtp(email)
        results.append(result)
    
    return {
        "success": True,
        "results": results,
        "total": len(results)
    }


@app.post("/api/domain-info")
async def get_domain_information(body: DomainInfoRequest, key_info: dict = Depends(auth.verify_api_key_dependency)):
    """Get enriched information about a domain (email provider, MX records, catch-all detection)."""
    info = get_domain_info(body.domain)
    return {
        "success": True,
        **info
    }


@app.post("/api/detect-catch-all")
async def check_catch_all(body: DomainInfoRequest, key_info: dict = Depends(auth.verify_api_key_dependency)):
    """Detect if domain uses catch-all email (accepts all addresses)."""
    result = detect_catch_all(body.domain)
    return {
        "success": True,
        **result
    }


@app.post("/api/bulk-upload-csv")
async def upload_csv_bulk(
    file: UploadFile = File(...),
    domain: Optional[str] = None,
    key_info: dict = Depends(auth.verify_api_key_dependency)
):
    """
    Upload CSV file with names for bulk email finding.
    
    CSV format: first_name, last_name, domain (domain column optional if provided as parameter)
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    # Read CSV content
    contents = await file.read()
    csv_content = contents.decode('utf-8')
    
    # Parse CSV
    has_domain_col = domain is None
    entries = parse_csv_upload(csv_content, has_domain_column=has_domain_col)
    
    if len(entries) > 500:
        raise HTTPException(status_code=400, detail="Maximum 500 rows per CSV upload")
    
    # Process each entry
    results = []
    for entry in entries:
        use_domain = entry.get('domain') or domain
        if not use_domain:
            continue
        
        patterns = generate_email_patterns(entry['first_name'], entry['last_name'], use_domain)
        results.append({
            "person": {"first_name": entry['first_name'], "last_name": entry['last_name']},
            "domain": use_domain,
            "emails": patterns,
            "total_results": len(patterns)
        })
    
    return {
        "success": True,
        "total_processed": len(results),
        "results": results
    }


@app.get("/api/export-csv/{job_type}")
async def export_csv(
    job_type: str,
    data: str = None,
    key_info: dict = Depends(auth.verify_api_key_dependency)
):
    """
    Export results as CSV.
    
    job_type: 'email-find' or 'verification'
    data: JSON string of results (pass via query param or have results stored by job_id)
    """
    # This is simplified - in production, you'd store job results and retrieve by job_id
    if not data:
        raise HTTPException(status_code=400, detail="No data provided for export")
    
    import json
    try:
        results = json.loads(data)
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON data")
    
    if job_type == "email-find":
        csv_content = export_results_to_csv(results)
    elif job_type == "verification":
        csv_content = export_verification_results_to_csv(results)
    else:
        raise HTTPException(status_code=400, detail="Invalid job_type. Use 'email-find' or 'verification'")
    
    # Return as downloadable CSV
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={job_type}_results.csv"}
    )
