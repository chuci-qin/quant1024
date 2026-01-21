"""
Module Base Class

所有 API 模块的基类，封装统一的 HTTP 请求逻辑。
每个模块通过 PATH_PREFIX 定义自己的 API 路径前缀。

设计模式：模板方法模式
- 基类定义请求骨架
- 子类定义具体路径和参数
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from ..exchange_1024ex import Exchange1024ex


class ModuleBase:
    """
    模块基类
    
    所有 API 模块继承此类，获得统一的 HTTP 请求能力。
    
    Attributes:
        PATH_PREFIX: API 路径前缀，子类需要覆盖
        _client: Exchange1024ex 客户端实例
    
    Example:
        >>> class PerpModule(ModuleBase):
        ...     PATH_PREFIX = "/api/v1/perp"
        ...     
        ...     def get_markets(self) -> List[Dict]:
        ...         return self._request("GET", "/markets")
    """
    
    PATH_PREFIX: str = ""
    
    def __init__(self, client: "Exchange1024ex") -> None:
        """
        初始化模块
        
        Args:
            client: Exchange1024ex 客户端实例，用于发送 HTTP 请求
        """
        self._client = client
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        auth_required: bool = True
    ) -> Any:
        """
        发送 HTTP 请求
        
        自动拼接 PATH_PREFIX 和 endpoint，委托给客户端执行请求。
        
        Args:
            method: HTTP 方法 (GET, POST, PUT, DELETE)
            endpoint: API 端点路径 (如 /markets, /orders)
            params: URL 查询参数
            data: 请求体数据 (JSON)
            auth_required: 是否需要认证
        
        Returns:
            API 响应数据
        
        Example:
            >>> # 实际请求路径: /api/v1/perp/markets/BTC-USDC/ticker
            >>> self._request("GET", "/markets/BTC-USDC/ticker")
        """
        path = f"{self.PATH_PREFIX}{endpoint}"
        return self._client._request(
            method=method,
            path=path,
            params=params,
            data=data,
            auth_required=auth_required
        )
    
    def _extract_data(self, result: Any) -> Any:
        """
        从响应中提取 data 字段
        
        处理标准响应格式：{"success": true, "data": [...]}
        
        Args:
            result: API 响应
        
        Returns:
            data 字段内容，或原始响应
        """
        if isinstance(result, dict):
            return result.get("data", result)
        return result

