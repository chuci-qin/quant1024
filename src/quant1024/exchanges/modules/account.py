"""
AccountModule - 账户管理模块

实现 /api/v1/accounts/me/ 下的所有 API 接口
"""

from typing import Any, Dict, List, Optional
from ._base import ModuleBase


class AccountModule(ModuleBase):
    """
    账户管理模块
    
    提供账户管理相关的 API 接口。
    """
    
    PATH_PREFIX = "/api/v1/accounts/me"
    
    # 将在 implement-account-module 任务中实现完整接口
    pass

