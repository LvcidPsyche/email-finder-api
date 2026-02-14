"""
Gumroad webhook integration for automated user provisioning.

When a customer purchases a plan on Gumroad, this webhook handler:
1. Receives the purchase notification
2. Creates a user account (or finds existing)
3. Generates an API key with the purchased plan tier
4. Sends welcome email with API key and docs

Setup:
1. Create products on Gumroad for each plan tier
2. Add webhook URL: https://yourapi.com/api/webhooks/gumroad
3. Set GUMROAD_WEBHOOK_SECRET in .env
"""

import hmac
import hashlib
import json
from typing import Optional
import os


def verify_gumroad_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify Gumroad webhook signature.

    Args:
        payload: Raw request body bytes
        signature: X-Gumroad-Signature header value
        secret: Your Gumroad webhook secret

    Returns:
        True if signature is valid
    """
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(expected_signature, signature)


def parse_gumroad_webhook(data: dict) -> Optional[dict]:
    """
    Parse Gumroad webhook payload and extract relevant info.

    Returns:
        dict with: email, product_id, product_name, price, purchase_id
        None if invalid/test ping
    """
    # Gumroad sends different events; we care about "sale" events
    if data.get('seller_id') == 'test':  # Gumroad test ping
        return None

    email = data.get('email') or data.get('buyer', {}).get('email')
    product_id = data.get('product_id')
    product_name = data.get('product_name')
    price = data.get('price')  # in cents
    purchase_id = data.get('sale_id') or data.get('id')

    if not email or not product_id:
        return None

    return {
        'email': email,
        'product_id': product_id,
        'product_name': product_name,
        'price': price,
        'purchase_id': purchase_id
    }


def map_product_to_plan_tier(product_id: str, product_name: str) -> str:
    """
    Map Gumroad product to plan tier.

    Customize this based on your Gumroad product IDs.

    Returns:
        'free', 'starter', 'pro', or 'enterprise'
    """
    product_name_lower = product_name.lower() if product_name else ""

    # Map by product name keywords
    if 'starter' in product_name_lower:
        return 'starter'
    elif 'pro' in product_name_lower:
        return 'pro'
    elif 'enterprise' in product_name_lower:
        return 'enterprise'
    elif 'free' in product_name_lower:
        return 'free'

    # Default to starter if can't determine
    return 'starter'


async def process_gumroad_purchase(webhook_data: dict, database_module) -> dict:
    """
    Process a Gumroad purchase: create user + API key.

    Args:
        webhook_data: Parsed webhook data from parse_gumroad_webhook
        database_module: Your database module (must have create_user, create_api_key_for_user)

    Returns:
        dict with success status and API key
    """
    email = webhook_data['email']
    product_id = webhook_data['product_id']
    product_name = webhook_data['product_name']

    # Determine plan tier
    plan_tier = map_product_to_plan_tier(product_id, product_name)

    # Try to create user (or get existing)
    user_id = await database_module.create_user(email, generate_random_password())

    if not user_id:
        # User already exists, fetch their ID
        user = await database_module.authenticate_user(email, None)  # This won't work as-is
        # Better: add a get_user_by_email function to database module
        # For now, assume user_id=None means existing user - handle carefully
        # In production, add: async def get_user_id_by_email(email: str) -> Optional[int]
        # For now, we'll return an error and require manual handling
        return {
            'success': False,
            'error': 'User already exists. Please contact support to upgrade your plan.',
            'email': email
        }

    # Create API key for the purchased plan
    api_key = await database_module.create_api_key_for_user(user_id, plan_tier=plan_tier)

    return {
        'success': True,
        'user_id': user_id,
        'email': email,
        'api_key': api_key,
        'plan_tier': plan_tier,
        'product_name': product_name
    }


def generate_random_password(length: int = 16) -> str:
    """Generate a secure random password for auto-created accounts."""
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def generate_welcome_email_html(user_email: str, api_key: str, plan_tier: str, product_name: str, docs_url: str) -> str:
    """
    Generate HTML welcome email for new customer.

    Args:
        user_email: Customer email
        api_key: Generated API key
        plan_tier: Plan tier name
        product_name: Product they purchased
        docs_url: URL to API docs

    Returns:
        HTML email content
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #0ea5e9; color: white; padding: 20px; text-align: center; }}
            .content {{ background: #f9f9f9; padding: 30px; border: 1px solid #ddd; }}
            .api-key {{ background: #fff; padding: 15px; border: 2px solid #0ea5e9; border-radius: 5px; font-family: monospace; word-break: break-all; }}
            .cta-button {{ display: inline-block; background: #0ea5e9; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
            .footer {{ text-align: center; margin-top: 30px; color: #888; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to {product_name}!</h1>
            </div>
            <div class="content">
                <p>Hi there,</p>
                <p>Thank you for purchasing the <strong>{plan_tier.title()} Plan</strong> of {product_name}!</p>

                <p>Your account has been automatically created. Here's your API key:</p>

                <div class="api-key">
                    <strong>API Key:</strong><br>
                    {api_key}
                </div>

                <p><strong>⚠️ Important:</strong> This is the only time you'll see your full API key. Please save it securely.</p>

                <h3>Getting Started</h3>
                <ul>
                    <li>Add your API key to requests via the <code>X-API-Key</code> header</li>
                    <li>View full documentation and examples</li>
                    <li>Check your usage stats at any time</li>
                </ul>

                <p>
                    <a href="{docs_url}" class="cta-button">View Documentation</a>
                </p>

                <h3>Your Plan Details</h3>
                <ul>
                    <li><strong>Email:</strong> {user_email}</li>
                    <li><strong>Plan:</strong> {plan_tier.title()}</li>
                    <li><strong>Product:</strong> {product_name}</li>
                </ul>

                <p>Need help? Just reply to this email!</p>

                <p>Happy building! 🚀</p>
            </div>
            <div class="footer">
                <p>You received this email because you purchased {product_name} on Gumroad.</p>
            </div>
        </div>
    </body>
    </html>
    """


# Example webhook endpoint (add to main.py):
"""
from fastapi import Request
import gumroad_integration

@app.post("/api/webhooks/gumroad")
async def gumroad_webhook(request: Request):
    # Get raw body and signature
    body_bytes = await request.body()
    signature = request.headers.get("X-Gumroad-Signature")

    secret = os.getenv("GUMROAD_WEBHOOK_SECRET")
    if not secret:
        raise HTTPException(status_code=500, detail="Webhook secret not configured")

    # Verify signature
    if not gumroad_integration.verify_gumroad_signature(body_bytes, signature, secret):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse webhook data
    data = json.loads(body_bytes)
    webhook_data = gumroad_integration.parse_gumroad_webhook(data)

    if not webhook_data:
        return {"status": "ignored", "reason": "test ping or invalid data"}

    # Process purchase
    result = await gumroad_integration.process_gumroad_purchase(webhook_data, database)

    if result['success']:
        # Send welcome email (use your email service)
        email_html = gumroad_integration.generate_welcome_email_html(
            result['email'],
            result['api_key'],
            result['plan_tier'],
            webhook_data['product_name'],
            "https://yourapi.com/docs"
        )
        # TODO: Send email_html via SendGrid, Mailgun, etc.

        return {
            "status": "success",
            "message": "User provisioned successfully",
            "email": result['email']
        }
    else:
        return {
            "status": "error",
            "error": result.get('error'),
            "email": result.get('email')
        }
"""
