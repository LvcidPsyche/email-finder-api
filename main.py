import dns.resolver
from fastapi import FastAPI, Request, HTTPException, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="Email Finder API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Valid API keys
VALID_API_KEYS = {"demo-key-2024"}


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


# --- Auth dependency ---

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


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
    """Check MX records for a domain using dnspython."""
    try:
        answers = dns.resolver.resolve(domain, "MX")
        mx_records = []
        for rdata in answers:
            mx_records.append({
                "priority": rdata.preference,
                "host": str(rdata.exchange).rstrip("."),
            })
        mx_records.sort(key=lambda x: x["priority"])
        return {
            "domain": domain,
            "has_mx": True,
            "accepts_email": True,
            "mx_records": mx_records,
            "record_count": len(mx_records),
        }
    except dns.resolver.NoAnswer:
        return {
            "domain": domain,
            "has_mx": False,
            "accepts_email": False,
            "mx_records": [],
            "record_count": 0,
            "error": "No MX records found",
        }
    except dns.resolver.NXDOMAIN:
        return {
            "domain": domain,
            "has_mx": False,
            "accepts_email": False,
            "mx_records": [],
            "record_count": 0,
            "error": "Domain does not exist",
        }
    except dns.resolver.NoNameservers:
        return {
            "domain": domain,
            "has_mx": False,
            "accepts_email": False,
            "mx_records": [],
            "record_count": 0,
            "error": "No nameservers available for domain",
        }
    except Exception as e:
        return {
            "domain": domain,
            "has_mx": False,
            "accepts_email": False,
            "mx_records": [],
            "record_count": 0,
            "error": str(e),
        }


# --- Routes ---

@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/find-email")
async def find_email(body: FindEmailRequest, api_key: str = Depends(verify_api_key)):
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
async def verify_domain(body: VerifyDomainRequest, api_key: str = Depends(verify_api_key)):
    domain = body.domain.lower().strip()
    if not domain:
        raise HTTPException(status_code=400, detail="domain is required")

    result = check_mx_records(domain)
    return {"success": True, **result}


@app.post("/api/bulk-find")
async def bulk_find(body: BulkFindRequest, api_key: str = Depends(verify_api_key)):
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
async def get_patterns(domain: str, api_key: str = Depends(verify_api_key)):
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
    uvicorn.run("main:app", host="0.0.0.0", port=8770, reload=True)
