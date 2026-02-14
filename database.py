"""
Shared database module for user management and API key tracking.
"""
import aiosqlite
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import Optional
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DB_PATH = os.getenv("DATABASE_URL", "sqlite:///./data.db").replace("sqlite:///", "")
JWT_SECRET = os.getenv("JWT_SECRET", "change-this-jwt-secret-in-production")
# Security check - fail if using default JWT secret
if JWT_SECRET == "change-this-jwt-secret-in-production":
    import sys
    print("\n\033[91mSECURITY ERROR: Using default JWT_SECRET!\033[0m")
    print("Set a secure JWT_SECRET in your .env file before running in production.")
    print("Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(32))'\n")
    sys.exit(1)
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DAYS = 30


async def init_database():
    """Initialize database tables."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Users table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)

        # API keys table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                key_hash TEXT UNIQUE NOT NULL,
                key_prefix TEXT NOT NULL,
                plan_tier TEXT DEFAULT 'free',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)

        # Usage logs table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS usage_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                api_key_id INTEGER NOT NULL,
                endpoint TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                response_time_ms INTEGER,
                status_code INTEGER,
                FOREIGN KEY (api_key_id) REFERENCES api_keys (id)
            )
        """)

        # Add demo key if it doesn't exist
        demo_key_hash = hashlib.sha256(b"demo-key-2024").hexdigest()
        await db.execute("""
            INSERT OR IGNORE INTO users (id, email, password_hash)
            VALUES (1, 'demo@example.com', 'demo')
        """)
        await db.execute("""
            INSERT OR IGNORE INTO api_keys (user_id, key_hash, key_prefix, plan_tier)
            VALUES (1, ?, 'demo-', 'free')
        """, (demo_key_hash,))

        await db.commit()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_jwt_token(user_id: int, email: str) -> str:
    """Create a JWT token for a user."""
    expiration = datetime.utcnow() + timedelta(days=JWT_EXPIRATION_DAYS)
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": expiration
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_jwt_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def generate_api_key() -> tuple[str, str, str]:
    """Generate a new API key.

    Returns:
        (full_key, key_hash, key_prefix)
    """
    prefix = secrets.token_hex(4)  # 8 chars
    suffix = secrets.token_hex(16)  # 32 chars
    full_key = f"{prefix}-{suffix}"
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()
    return full_key, key_hash, prefix


async def create_user(email: str, password: str) -> Optional[int]:
    """Create a new user.

    Returns:
        user_id if successful, None if email already exists
    """
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            cursor = await db.execute("""
                INSERT INTO users (email, password_hash)
                VALUES (?, ?)
            """, (email, hash_password(password)))
            await db.commit()
            return cursor.lastrowid
        except aiosqlite.IntegrityError:
            return None


async def authenticate_user(email: str, password: str) -> Optional[dict]:
    """Authenticate a user by email and password.

    Returns:
        User dict with id and email if successful, None otherwise
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT id, email, password_hash, is_active
            FROM users
            WHERE email = ?
        """, (email,)) as cursor:
            user = await cursor.fetchone()

            if not user or not user["is_active"]:
                return None

            if verify_password(password, user["password_hash"]):
                return {"id": user["id"], "email": user["email"]}
            return None


async def create_api_key_for_user(user_id: int, plan_tier: str = "free") -> str:
    """Create a new API key for a user.

    Returns:
        The full API key (only shown once)
    """
    full_key, key_hash, key_prefix = generate_api_key()

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO api_keys (user_id, key_hash, key_prefix, plan_tier)
            VALUES (?, ?, ?, ?)
        """, (user_id, key_hash, key_prefix, plan_tier))
        await db.commit()

    return full_key


async def verify_api_key(api_key: str) -> Optional[dict]:
    """Verify an API key and return key info.

    Returns:
        Dict with api_key_id, user_id, plan_tier if valid, None otherwise
    """
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT ak.id, ak.user_id, ak.plan_tier, u.is_active as user_active
            FROM api_keys ak
            JOIN users u ON ak.user_id = u.id
            WHERE ak.key_hash = ? AND ak.is_active = 1
        """, (key_hash,)) as cursor:
            row = await cursor.fetchone()

            if not row or not row["user_active"]:
                return None

            return {
                "api_key_id": row["id"],
                "user_id": row["user_id"],
                "plan_tier": row["plan_tier"]
            }


async def log_usage(api_key_id: int, endpoint: str, response_time_ms: int, status_code: int):
    """Log an API usage event."""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO usage_logs (api_key_id, endpoint, response_time_ms, status_code)
            VALUES (?, ?, ?, ?)
        """, (api_key_id, endpoint, response_time_ms, status_code))
        await db.commit()


async def get_usage_stats(api_key_id: int, days: int = 1) -> dict:
    """Get usage statistics for an API key.

    Returns:
        Dict with total_calls, calls_today, plan_tier, rate_limit
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row

        # Get total calls in the specified time period
        async with db.execute("""
            SELECT COUNT(*) as count
            FROM usage_logs
            WHERE api_key_id = ?
            AND timestamp >= datetime('now', ? || ' days')
        """, (api_key_id, -days)) as cursor:
            row = await cursor.fetchone()
            total_calls = row["count"] if row else 0

        # Get plan tier
        async with db.execute("""
            SELECT plan_tier FROM api_keys WHERE id = ?
        """, (api_key_id,)) as cursor:
            row = await cursor.fetchone()
            plan_tier = row["plan_tier"] if row else "free"

        # Get rate limits from env
        rate_limits = {
            "free": int(os.getenv("RATE_LIMIT_FREE", "10")),
            "starter": int(os.getenv("RATE_LIMIT_STARTER", "500")),
            "pro": int(os.getenv("RATE_LIMIT_PRO", "5000")),
            "enterprise": int(os.getenv("RATE_LIMIT_ENTERPRISE", "999999"))
        }

        limit = rate_limits.get(plan_tier, 10)
        remaining = max(0, limit - total_calls)

        return {
            "total_calls": total_calls,
            "plan_tier": plan_tier,
            "rate_limit": limit,
            "remaining": remaining,
            "period_days": days
        }


async def list_api_keys_for_user(user_id: int) -> list[dict]:
    """List all API keys for a user.

    Returns:
        List of dicts with key_prefix, plan_tier, created_at, is_active
    """
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT id, key_prefix, plan_tier, created_at, is_active
            FROM api_keys
            WHERE user_id = ?
            ORDER BY created_at DESC
        """, (user_id,)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
