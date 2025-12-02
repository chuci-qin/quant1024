"""
Authentication for 1024ex API

Supports HMAC-SHA256 authentication as per OpenAPI spec:
- Header: X-EXCHANGE-API-KEY (API Key)
- Header: X-SIGNATURE (HMAC-SHA256 signature)
- Header: X-TIMESTAMP (Unix timestamp in milliseconds)
- Header: X-RECV-WINDOW (Optional, default 5000ms)

API Documentation: https://api.1024ex.com/api-docs/openapi.json
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
    生成 HMAC-SHA256 签名
    
    Signature = HMAC-SHA256(secret_key, timestamp + method + path + body)
    
    Args:
        secret_key: API Secret Key
        timestamp: 时间戳（毫秒字符串）
        method: HTTP 方法（GET, POST, PUT, DELETE）
        path: API 路径（如 /api/v1/orders）
        body: 请求体（JSON 字符串，GET 请求为空）
    
    Returns:
        HMAC-SHA256 签名（十六进制字符串）
    """
    # 构造签名消息：timestamp + method + path + body
    message = f"{timestamp}{method}{path}{body}"
    
    # 生成 HMAC-SHA256 签名
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
    body: str = "",
    recv_window: int = 5000
) -> Dict[str, str]:
    """
    生成 HMAC-SHA256 认证 Headers
    
    符合 1024 Exchange API 规范:
    - X-EXCHANGE-API-KEY: API Key
    - X-SIGNATURE: HMAC-SHA256(secret_key, timestamp + method + path + body)
    - X-TIMESTAMP: Unix timestamp in milliseconds
    - X-RECV-WINDOW: Request validity window (default 5000ms)
    
    Args:
        api_key: Exchange API Key
        secret_key: Exchange Secret Key
        method: HTTP 方法 (GET, POST, PUT, DELETE)
        path: API 路径 (如 /api/v1/orders)
        body: 请求体 JSON 字符串 (GET 请求为空)
        recv_window: 请求有效窗口（毫秒，默认 5000）
    
    Returns:
        包含完整认证信息的 Headers 字典
    """
    timestamp = str(int(time.time() * 1000))
    signature = generate_signature(secret_key, timestamp, method, path, body)
    
    return {
        "Content-Type": "application/json",
        "X-EXCHANGE-API-KEY": api_key,
        "X-SIGNATURE": signature,
        "X-TIMESTAMP": timestamp,
        "X-RECV-WINDOW": str(recv_window)
    }


def get_simple_auth_headers(api_key: str) -> Dict[str, str]:
    """
    生成简单 API Key 认证 Headers（仅用于公开端点或测试）
    
    注意：大部分需要认证的端点都需要 HMAC 签名，
    请优先使用 get_auth_headers() 函数。
    
    Args:
        api_key: Exchange API Key
    
    Returns:
        包含 X-EXCHANGE-API-KEY 的 Headers 字典
    """
    return {
        "X-EXCHANGE-API-KEY": api_key,
        "Content-Type": "application/json"
    }
