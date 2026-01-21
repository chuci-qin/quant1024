"""
PerpModule - 永续合约模块

实现 /api/v1/perp/ 下的所有 API 接口
"""

from typing import Any, Dict, List, Optional
from ._base import ModuleBase


class PerpModule(ModuleBase):
    """
    永续合约模块
    
    提供永续合约交易相关的所有 API 接口。
    """
    
    PATH_PREFIX = "/api/v1/perp"
    
    # 将在 implement-perp-module 任务中实现完整接口
    pass

