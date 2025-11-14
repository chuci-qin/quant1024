"""
Runtime 监控配置类型定义
"""

import os
import uuid
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


@dataclass
class RuntimeConfig:
    """
    Runtime 监控配置（简化版）
    
    设计原则：
    - 只有 api_key 是必填的
    - 其他都自动处理或可选
    - api_base_url 默认指向 1024Quant 平台（与交易所无关）
    """
    
    # 必填字段
    api_key: str  # 记录服务的 API Key
    
    # 自动生成/读取的字段
    runtime_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    strategy_id: Optional[str] = field(default_factory=lambda: os.getenv('STRATEGY_ID'))
    
    # 可选配置字段
    api_base_url: str = "https://api.1024quant.com"  # 默认：1024Quant 平台 API
    environment: str = field(default_factory=lambda: os.getenv('ENVIRONMENT', 'local'))
    sdk_version: Optional[str] = None
    extra_metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """初始化后处理"""
        # 自动填充 SDK 版本
        if not self.sdk_version:
            try:
                from quant1024 import __version__
                self.sdk_version = __version__
            except:
                self.sdk_version = "unknown"
        
        # 支持从环境变量覆盖 api_base_url
        env_base_url = os.getenv('API_BASE_URL')
        if env_base_url:
            self.api_base_url = env_base_url
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "runtime_id": self.runtime_id,
            "strategy_id": self.strategy_id,
            "api_base_url": self.api_base_url,
            "environment": self.environment,
            "sdk_version": self.sdk_version,
            "extra_metadata": self.extra_metadata
        }

