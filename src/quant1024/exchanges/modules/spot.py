"""
SpotModule - 现货交易模块

实现 /api/v1/spot/ 下的所有 API 接口
"""

from typing import Any, Dict, List, Optional
from ._base import ModuleBase


class SpotModule(ModuleBase):
    """
    现货交易模块
    
    提供现货交易相关的所有 API 接口。
    """
    
    PATH_PREFIX = "/api/v1/spot"
    
    # 将在 implement-spot-module 任务中实现完整接口
    pass

