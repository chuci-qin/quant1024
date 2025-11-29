"""
Authentication for 1024ex API

Supports two authentication methods:
1. Simple API Key (X-API-KEY header) - default
2. HMAC-SHA256 signing (for backward compatibility)
"""

import hmac
import hashlib
import time
from typing import Dict


def generate_signature(
    api_secret: str,
    timestamp: str,
    method: str,
    path: str,
    body: str = ""
) -> str:
    """
    生成 HMAC-SHA256 签名
    
    Args:
        api_secret: API Secret Key
        timestamp: 时间戳（毫秒）
        method: HTTP 方法（GET, POST, PUT, DELETE）
        path: API 路径（如 /api/v1/markets）
        body: 请求体（JSON 字符串，GET 请求为空）
    
    Returns:
        HMAC-SHA256 签名（十六进制字符串）
    """
    # 构造签名消息：timestamp + method + path + body
    message = f"{timestamp}{method}{path}{body}"
    
    # 生成 HMAC-SHA256 签名
    signature = hmac.new(
        api_secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return signature


def get_auth_headers(
    api_key: str,
    api_secret: str = "",
    method: str = "",
    path: str = "",
    body: str = "",
    use_simple_auth: bool = True
) -> Dict[str, str]:
    """
    生成认证 Headers
    
    Args:
        api_key: API Key
        api_secret: API Secret Key (optional for simple auth)
        method: HTTP 方法 (optional for simple auth)
        path: API 路径 (optional for simple auth)
        body: 请求体 (optional for simple auth)
        use_simple_auth: 是否使用简单 API Key 认证（默认 True）
    
    Returns:
        包含认证信息的 Headers 字典
    """
    headers = {"Content-Type": "application/json"}
    
    if use_simple_auth:
        # 简单 API Key 认证（符合 OpenAPI 规范）
        headers["X-API-KEY"] = api_key
    else:
        # HMAC-SHA256 签名认证（保留兼容性）
        timestamp = str(int(time.time() * 1000))
        signature = generate_signature(api_secret, timestamp, method, path, body)
        headers["API-KEY"] = api_key
        headers["API-TIMESTAMP"] = timestamp
        headers["API-SIGNATURE"] = signature
    
    return headers


def get_simple_auth_headers(api_key: str) -> Dict[str, str]:
    """
    生成简单 API Key 认证 Headers（符合 OpenAPI 规范）
    
    Args:
        api_key: API Key
    
    Returns:
        包含 X-API-KEY 的 Headers 字典
    """
    return {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }

