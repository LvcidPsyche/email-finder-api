# SaaS Products Build Guide

## Current Status: MVP Complete

All 4 products have working FastAPI backends, landing pages, and are deployed.

| Product | Port | GitHub | Landing | API | Demo |
|---------|------|--------|---------|-----|------|
| Email Finder API | 8770 | LvcidPsyche/email-finder-api | Done | Done | Done |
| Content Repurposer | 8771 | LvcidPsyche/content-repurposer | Done | Done | Done |
| GEO Monitor | 8772 | LvcidPsyche/geo-monitor | Done | Done | Done |
| Proposal Generator | 8773 | LvcidPsyche/proposal-generator | Done | Done | Done |

---

## PHASE 1: Shared Infrastructure (All 4 Products)

These items apply to ALL products. Build once, copy to each.

### 1.1 Environment Config (.env support)
- [ ] Add python-dotenv to requirements.txt
- [ ] Create .env.example with: PORT, API_KEY, DATABASE_URL, CORS_ORIGINS, LOG_LEVEL
- [ ] Replace hardcoded values in main.py with env vars
- [ ] Add .env to .gitignore

### 1.2 SQLite Database + User System
- [ ] Add sqlite3/aiosqlite to each project
- [ ] Create tables: users, api_keys, usage_logs
- [ ] User registration endpoint: POST /api/auth/register (email, password)
- [ ] User login endpoint: POST /api/auth/login (returns JWT token)
- [ ] API key generation: POST /api/auth/create-key (requires JWT)
- [ ] Replace hardcoded "demo-key-2024" with DB-backed key lookup
- [ ] Keep "demo-key-2024" as a free-tier demo key with 10 calls/day limit

### 1.3 Usage Tracking & Rate Limiting
- [ ] Log every API call: timestamp, api_key, endpoint, response_time
- [ ] Rate limiter middleware: Free=10/day, Starter=100/day, Pro=1000/day, Enterprise=unlimited
- [ ] GET /api/usage endpoint showing call count, remaining quota
- [ ] Return X-RateLimit-Remaining and X-RateLimit-Reset headers

### 1.4 Health Check & Monitoring
- [ ] GET /health endpoint returning {"status": "ok", "uptime": ..., "version": ...}
- [ ] Basic request logging with structured JSON output

### 1.5 Dockerfile
- [ ] Create Dockerfile for each project (python:3.12-slim base)
- [ ] docker-compose.yml in workspace root to run all 4 together

### 1.6 Nginx + Domain Setup
- [ ] Create nginx server blocks for each product domain
- [ ] SSL via Let's Encrypt (certbot)
- [ ] Proxy pass to localhost:877X

### 1.7 Systemd Services
- [ ] Create .service file for each app so they auto-start on boot
- [ ] Enable and start all 4 services

### 1.8 README.md for Each Repo
- [ ] Project description
- [ ] API documentation with all endpoints
- [ ] Setup instructions (local dev)
- [ ] Environment variables reference
- [ ] Example curl commands

---

## PHASE 2: Product-Specific Enhancements

### 2.1 Email Finder API (port 8770)

**Currently has:**
- POST /api/find-email (pattern generation + MX verification)
- POST /api/verify-domain (MX record check via dnspython)
- POST /api/bulk-find (up to 100 names)
- GET /api/patterns/{domain}
- Landing page with live demo

**Still needs:**
- [ ] SMTP verification endpoint: POST /api/verify-email - actually connect to SMTP to check if mailbox exists (catch-all detection)
- [ ] MX record caching (cache lookups for 1 hour to reduce DNS queries)
- [ ] CSV bulk upload endpoint: POST /api/bulk-upload - accept CSV file with name,domain columns
- [ ] Export results as CSV: GET /api/export/{job_id}
- [ ] Webhook callback: optional webhook_url in bulk requests, POST results when done
- [ ] Domain enrichment: GET /api/domain-info/{domain} - return company info, email provider, catch-all status
- [ ] Landing page: add API docs tab with interactive Swagger-like tester
- [ ] Landing page: add "Trusted by X users" social proof section

### 2.2 Content Repurposer (port 8771)

**Currently has:**
- POST /api/repurpose (twitter, linkedin, email, summary formats)
- POST /api/extract-points (key bullet points)
- POST /api/headline-variants (5 headline styles)
- GET /api/formats
- Landing page with live demo + tabbed results

**Still needs:**
- [ ] Add more output formats:
  - "instagram" - caption with emojis and 30 hashtags
  - "youtube_description" - SEO-optimized video description
  - "blog_outline" - H2/H3 structured outline from content
  - "podcast_script" - conversational script version
- [ ] Content history: save repurposed outputs per API key, GET /api/history
- [ ] Word count and readability score in responses
- [ ] Tone adjustment parameter: "professional", "casual", "humorous", "urgent"
- [ ] POST /api/batch-repurpose - accept array of content pieces
- [ ] Landing page: add before/after examples section
- [ ] Landing page: add format preview cards showing sample outputs

### 2.3 GEO Monitor (port 8772)

**Currently has:**
- POST /api/check-ranking (simulated ranking data, seeded by hash)
- POST /api/monitor (create monitoring setup, in-memory)
- GET /api/locations (50 cities)
- GET /api/report/{monitor_id} (7-day historical data)
- Landing page with demo + ranking table + animated counters

**Still needs:**
- [ ] Persist monitors to SQLite (currently in-memory, lost on restart)
- [ ] GET /api/monitors - list all monitors for an API key
- [ ] DELETE /api/monitor/{id} - remove a monitor
- [ ] PUT /api/monitor/{id} - update keywords/locations
- [ ] GET /api/report/{id}/csv - export report as CSV
- [ ] Alert thresholds: POST /api/alerts - notify when rank drops below position X
- [ ] Competitor comparison: add competitor_domains field to monitor
- [ ] Historical trend charts data: GET /api/trends/{monitor_id}?days=30
- [ ] Landing page: add interactive chart (Chart.js) in demo section showing 7-day trend
- [ ] Landing page: add competitor comparison visual

### 2.4 Proposal Generator (port 8773)

**Currently has:**
- POST /api/generate (full structured proposal JSON)
- POST /api/generate-pdf (HTML formatted for print/PDF)
- GET /api/templates (5 project types)
- POST /api/customize (basic rule-based modifications)
- Landing page with form + live proposal preview

**Still needs:**
- [ ] Actual PDF generation: use weasyprint or reportlab to return real PDF binary
- [ ] Proposal storage: save generated proposals to DB, GET /api/proposals (list), GET /api/proposals/{id}
- [ ] Custom branding: POST /api/branding - upload logo URL, company name, colors (stored per API key)
- [ ] Duplicate/clone: POST /api/proposals/{id}/clone
- [ ] Template customization: POST /api/templates/custom - create custom scope items and timeline
- [ ] Version history: track edits to a proposal
- [ ] Cover page with client logo in PDF output
- [ ] Acceptance workflow: unique link for client to view and accept proposal
- [ ] Landing page: add PDF download button in demo
- [ ] Landing page: add template gallery showing all 5 types

---

## PHASE 3: Growth & Monetization

### 3.1 Gumroad Integration (All Products)
- [ ] Create actual Gumroad products for each pricing tier
- [ ] Add Gumroad webhook endpoint: POST /api/webhooks/gumroad
- [ ] On successful purchase: auto-create user account + API key
- [ ] Send welcome email with API key and docs link
- [ ] License validation: check Gumroad license key on API requests

### 3.2 Dashboard UI (All Products)
- [ ] /dashboard route - simple HTML dashboard for logged-in users
- [ ] Show: API key, usage stats, remaining quota, plan info
- [ ] API key rotation (regenerate key)
- [ ] Upgrade plan button (links to Gumroad)

### 3.3 Marketing Pages (All Products)
- [ ] /docs route - full API documentation page
- [ ] /changelog route - product updates
- [ ] Add OpenGraph meta tags and Twitter cards to landing pages
- [ ] Add Google Analytics / Plausible snippet
- [ ] Add Crisp or Tawk.to chat widget

### 3.4 SEO & Content
- [ ] Optimize landing page title/meta description for each product
- [ ] Add structured data (JSON-LD) for SoftwareApplication schema
- [ ] Create /blog section with 3 SEO-optimized posts per product
- [ ] Sitemap.xml for each product

---

## PHASE 4: Polish & Scale

### 4.1 Testing
- [ ] pytest test suite for each product (API endpoint tests)
- [ ] Test auth, rate limiting, error handling
- [ ] CI/CD with GitHub Actions

### 4.2 Performance
- [ ] Add response caching for expensive endpoints
- [ ] Connection pooling for database
- [ ] Async where possible

### 4.3 Security Hardening
- [ ] Input validation and sanitization on all endpoints
- [ ] HTTPS-only enforcement
- [ ] API key hashing in database (store hashed, compare on request)
- [ ] Request size limits
- [ ] CORS lockdown (specific origins instead of *)

---

## Build Order (Recommended)

```
PHASE 1 (Infrastructure) - Do first, applies to all 4
  1.1 .env config
  1.2 Database + auth
  1.3 Rate limiting
  1.4 Health checks
  1.5 Dockerfiles
  1.6 Nginx + SSL
  1.7 Systemd services
  1.8 READMEs

PHASE 2 (Product features) - Do per-product, push after each
  2.1 Email Finder enhancements
  2.2 Content Repurposer enhancements
  2.3 GEO Monitor enhancements
  2.4 Proposal Generator enhancements

PHASE 3 (Monetization) - Critical for revenue
  3.1 Gumroad webhooks (auto-provisioning)
  3.2 User dashboards
  3.3 Marketing pages
  3.4 SEO

PHASE 4 (Scale) - When you have paying users
  4.1 Tests
  4.2 Performance
  4.3 Security
```

---

## Quick Reference

| Product | Dir | Port | Repo |
|---------|-----|------|------|
| Email Finder API | /home/botuser/.openclaw/workspace/email-finder-api | 8770 | LvcidPsyche/email-finder-api |
| Content Repurposer | /home/botuser/.openclaw/workspace/content-repurposer | 8771 | LvcidPsyche/content-repurposer |
| GEO Monitor | /home/botuser/.openclaw/workspace/geo-monitor | 8772 | LvcidPsyche/geo-monitor |
| Proposal Generator | /home/botuser/.openclaw/workspace/proposal-generator | 8773 | LvcidPsyche/proposal-generator |

**Start a product:** `cd <dir> && ./start.sh`
**Push changes:** `cd <dir> && git add -A && git commit -m "msg" && git push`
