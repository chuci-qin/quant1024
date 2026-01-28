"""
Authentication for 1024ex Public API

Implements HMAC-SHA256 authentication as per 1024 Exchange Public API v4.1.0 specification.

## Headers Required for Authenticated Endpoints

- `X-API-KEY` or `X-TRADING-API-KEY`: Your Trading API Key
- `X-SIGNATURE`: HMAC-SHA256 signature (hex-encoded)
- `X-TIMESTAMP`: Unix timestamp in milliseconds

## Signature Calculation

```
message = timestamp + METHOD + path + body
signature = hex(HMAC-SHA256(secret_key, message))
```

Where:
- `timestamp`: Unix timestamp in milliseconds (string)
- `METHOD`: HTTP method in UPPERCASE (GET, POST, PUT, DELETE)
- `path`: API endpoint path (e.g., /api/v1/perp/orders)
- `body`: Request body JSON string (empty string for GET requests)

## Timestamp Validation

The timestamp must be within 30 seconds of the server time.
"""

import hmac
import hashlib
import time
from typing import Dict


def generate_signature(
    secret_key: str,
    timestamp: str,
    method: str,
    path: str,
    body: str = ""
) -> str:
    """
    Generate HMAC-SHA256 signature for API authentication.
    
    Formula: signature = hex(HMAC-SHA256(secret_key, timestamp + METHOD + path + body))
    
    Args:
        secret_key: Trading API Secret Key
        timestamp: Unix timestamp in milliseconds (string)
        method: HTTP method (will be converted to uppercase)
        path: API endpoint path (e.g., /api/v1/perp/orders)
        body: Request body JSON string (empty for GET requests)
    
    Returns:
        HMAC-SHA256 signature as hex string
    
    Example:
        >>> sig = generate_signature(
        ...     secret_key="abc123",
        ...     timestamp="1735084800000",
        ...     method="POST",
        ...     path="/api/v1/perp/orders",
        ...     body='{"market":"BTC-USDC","side":"long"}'
        ... )
    """
    # Build signature message: timestamp + METHOD(uppercase) + path + body
    # Backend uses method.to_uppercase() so we must match
    message = f"{timestamp}{method.upper()}{path}{body}"
    
    # Generate HMAC-SHA256 signature
    signature = hmac.new(
        secret_key.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return signature


def get_auth_headers(
    api_key: str,
    secret_key: str,
    method: str,
    path: str,
    body: str = ""
) -> Dict[str, str]:
    """
    Generate authentication headers for 1024 Exchange API.
    
    Complies with 1024 Exchange Public API v4.1.0 specification:
    - X-TRADING-API-KEY: Your Trading API Key
    - X-SIGNATURE: HMAC-SHA256 signature
    - X-TIMESTAMP: Unix timestamp in milliseconds
    
    Args:
        api_key: Trading API Key (starts with "1024_" prefix)
        secret_key: Trading API Secret Key
        method: HTTP method (GET, POST, PUT, DELETE)
        path: API endpoint path (e.g., /api/v1/perp/orders)
        body: Request body JSON string (empty for GET requests)
    
    Returns:
        Dict with complete authentication headers
    
    Example:
        >>> headers = get_auth_headers(
        ...     api_key="1024_abc123...",
        ...     secret_key="secret123...",
        ...     method="GET",
        ...     path="/api/v1/perp/positions",
        ...     body=""
        ... )
        >>> # Use headers in request
        >>> requests.get(url, headers=headers)
    
    Note:
        The timestamp is validated by the server (must be within 30 seconds).
        Method is automatically converted to uppercase for signature.
    """
    timestamp = str(int(time.time() * 1000))
    signature = generate_signature(secret_key, timestamp, method, path, body)
    
    return {
        "Content-Type": "application/json",
        "X-TRADING-API-KEY": api_key,
        "X-SIGNATURE": signature,
        "X-TIMESTAMP": timestamp,
    }


def get_simple_auth_headers(api_key: str) -> Dict[str, str]:
    """
    Generate simple API Key headers (for public endpoints or testing only).
    
    WARNING: Most authenticated endpoints require HMAC signature.
    Use get_auth_headers() instead for authenticated requests.
    
    Args:
        api_key: Trading API Key
    
    Returns:
        Dict with X-TRADING-API-KEY header
    """
    return {
        "X-TRADING-API-KEY": api_key,
        "Content-Type": "application/json"
    }


def verify_signature(
    secret_key: str,
    timestamp: str,
    method: str,
    path: str,
    body: str,
    signature: str
) -> bool:
    """
    Verify an HMAC-SHA256 signature.
    
    Useful for testing or webhook verification.
    
    Args:
        secret_key: Trading API Secret Key
        timestamp: Unix timestamp in milliseconds (string)
        method: HTTP method
        path: API endpoint path
        body: Request body JSON string
        signature: Signature to verify (hex string)
    
    Returns:
        True if signature is valid, False otherwise
    """
    expected = generate_signature(secret_key, timestamp, method, path, body)
    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(expected, signature)
