"""
Admin dashboard and monitoring endpoints.
"""
import os
from typing import Optional
from fastapi import HTTPException, Header
import aiosqlite


ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "change-this-admin-key")


def verify_admin_key(x_admin_key: Optional[str] = Header(None)):
    """Verify admin API key."""
    if not x_admin_key or x_admin_key != ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Admin access denied")
    return x_admin_key


async def get_system_stats(db_path: str = "./data.db"):
    """Get system-wide statistics."""
    async with aiosqlite.connect(db_path) as db:
        # Total users
        async with db.execute("SELECT COUNT(*) FROM users WHERE is_active = 1") as cursor:
            row = await cursor.fetchone()
            total_users = row[0] if row else 0
        
        # Total API keys
        async with db.execute("SELECT COUNT(*) FROM api_keys WHERE is_active = 1") as cursor:
            row = await cursor.fetchone()
            total_keys = row[0] if row else 0
        
        # API keys by plan
        async with db.execute("""
            SELECT plan_tier, COUNT(*) as count
            FROM api_keys
            WHERE is_active = 1
            GROUP BY plan_tier
        """) as cursor:
            plan_distribution = {}
            async for row in cursor:
                plan_distribution[row[0]] = row[1]
        
        # Total requests (last 24 hours)
        async with db.execute("""
            SELECT COUNT(*) 
            FROM usage_logs 
            WHERE timestamp >= datetime('now', '-1 day')
        """) as cursor:
            row = await cursor.fetchone()
            requests_24h = row[0] if row else 0
        
        # Total requests (last 7 days)
        async with db.execute("""
            SELECT COUNT(*) 
            FROM usage_logs 
            WHERE timestamp >= datetime('now', '-7 days')
        """) as cursor:
            row = await cursor.fetchone()
            requests_7d = row[0] if row else 0
        
        # Average response time
        async with db.execute("""
            SELECT AVG(response_time_ms) 
            FROM usage_logs 
            WHERE timestamp >= datetime('now', '-1 day')
            AND response_time_ms IS NOT NULL
        """) as cursor:
            row = await cursor.fetchone()
            avg_response_time = round(row[0], 2) if row and row[0] else 0
        
        # Top endpoints
        async with db.execute("""
            SELECT endpoint, COUNT(*) as count
            FROM usage_logs
            WHERE timestamp >= datetime('now', '-7 days')
            GROUP BY endpoint
            ORDER BY count DESC
            LIMIT 10
        """) as cursor:
            top_endpoints = []
            async for row in cursor:
                top_endpoints.append({"endpoint": row[0], "count": row[1]})
        
        # Error rate
        async with db.execute("""
            SELECT 
                COUNT(CASE WHEN status_code >= 400 THEN 1 END) as errors,
                COUNT(*) as total
            FROM usage_logs
            WHERE timestamp >= datetime('now', '-1 day')
        """) as cursor:
            row = await cursor.fetchone()
            errors = row[0] if row else 0
            total = row[1] if row else 1
            error_rate = round((errors / total * 100) if total > 0 else 0, 2)
        
        return {
            "users": {
                "total": total_users,
                "total_api_keys": total_keys,
                "plan_distribution": plan_distribution
            },
            "requests": {
                "last_24h": requests_24h,
                "last_7d": requests_7d,
                "avg_response_time_ms": avg_response_time
            },
            "performance": {
                "error_rate_percent": error_rate,
                "top_endpoints": top_endpoints
            }
        }


async def get_recent_users(db_path: str = "./data.db", limit: int = 20):
    """Get recently registered users."""
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT u.id, u.email, u.created_at, 
                   k.plan_tier, k.created_at as key_created
            FROM users u
            LEFT JOIN api_keys k ON u.id = k.user_id
            WHERE u.is_active = 1
            ORDER BY u.created_at DESC
            LIMIT ?
        """, (limit,)) as cursor:
            users = []
            async for row in cursor:
                users.append({
                    "id": row["id"],
                    "email": row["email"],
                    "created_at": row["created_at"],
                    "plan_tier": row["plan_tier"],
                    "key_created": row["key_created"]
                })
            return users


async def get_usage_by_user(db_path: str = "./data.db", limit: int = 20):
    """Get top users by request volume."""
    async with aiosqlite.connect(db_path) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT 
                u.email,
                k.plan_tier,
                COUNT(l.id) as total_requests,
                MAX(l.timestamp) as last_request
            FROM users u
            JOIN api_keys k ON u.id = k.user_id
            LEFT JOIN usage_logs l ON k.id = l.api_key_id
            WHERE u.is_active = 1
            AND l.timestamp >= datetime('now', '-7 days')
            GROUP BY u.id
            ORDER BY total_requests DESC
            LIMIT ?
        """, (limit,)) as cursor:
            users = []
            async for row in cursor:
                users.append({
                    "email": row["email"],
                    "plan_tier": row["plan_tier"],
                    "total_requests": row["total_requests"],
                    "last_request": row["last_request"]
                })
            return users
