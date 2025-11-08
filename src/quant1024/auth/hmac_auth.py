"""
HMAC-SHA256 authentication for 1024ex API
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
    api_secret: str,
    method: str,
    path: str,
    body: str = ""
) -> Dict[str, str]:
    """
    生成认证 Headers
    
    Args:
        api_key: API Key
        api_secret: API Secret Key
        method: HTTP 方法
        path: API 路径
        body: 请求体
    
    Returns:
        包含认证信息的 Headers 字典
    """
    # 生成时间戳（毫秒）
    timestamp = str(int(time.time() * 1000))
    
    # 生成签名
    signature = generate_signature(api_secret, timestamp, method, path, body)
    
    # 返回 Headers
    return {
        "API-KEY": api_key,
        "API-TIMESTAMP": timestamp,
        "API-SIGNATURE": signature,
        "Content-Type": "application/json"
    }

