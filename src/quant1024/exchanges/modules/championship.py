"""
ChampionshipModule - 锦标赛模块

实现 /api/v1/championships/ 下的所有 API 接口，包括：
- 锦标赛列表
- 锦标赛详情
- 排行榜
- 用户排名
- Top 3 英雄区数据
"""

from typing import Any, Dict, List, Optional
from ._base import ModuleBase


class ChampionshipModule(ModuleBase):
    """
    锦标赛模块
    
    提供锦标赛排行榜相关的 API 接口。
    
    Example:
        >>> exchange = Exchange1024ex(api_key="xxx", secret_key="xxx")
        >>> exchange.championship.list_championships(status="active")
        >>> exchange.championship.get_leaderboard("weekly-pnl")
    """
    
    PATH_PREFIX = "/api/v1/championships"
    
    def list_championships(
        self,
        status: Optional[str] = None,
        championship_type: Optional[str] = None,
        period: Optional[str] = None,
        featured_only: bool = False,
        offset: int = 0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        获取锦标赛列表
        
        Args:
            status: 状态过滤 (draft/upcoming/active/ended/cancelled)
            championship_type: 类型过滤 (ex_only/prediction_only/mixed)
            period: 周期过滤 (permanent/weekly/monthly/quarterly/annual/custom)
            featured_only: 只显示推荐的锦标赛
            offset: 偏移量
            limit: 返回数量
        """
        params: Dict[str, Any] = {"offset": offset, "limit": limit}
        if status:
            params["status"] = status
        if championship_type:
            params["type"] = championship_type
        if period:
            params["period"] = period
        if featured_only:
            params["featured_only"] = featured_only
        result = self._request("GET", "", params=params, auth_required=False)
        return self._extract_data(result)
    
    def get_championship(self, slug: str) -> Dict[str, Any]:
        """
        获取锦标赛详情
        
        Args:
            slug: 锦标赛 slug 或 ID
        """
        return self._request("GET", f"/{slug}", auth_required=False)
    
    def get_leaderboard(
        self,
        slug: str,
        sort_by: Optional[str] = None,
        period: Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取排行榜
        
        Args:
            slug: 锦标赛 slug 或 ID
            sort_by: 排序字段 (pnl/roi/volume/win_rate/trades)
            period: 时间周期 (24h/7d/30d/all)
            offset: 偏移量
            limit: 返回数量
            search: 搜索用户名或钱包地址
        """
        params: Dict[str, Any] = {"offset": offset, "limit": limit}
        if sort_by:
            params["sort_by"] = sort_by
        if period:
            params["period"] = period
        if search:
            params["search"] = search
        return self._request("GET", f"/{slug}/leaderboard", params=params, auth_required=False)
    
    def get_my_rank(self, slug: str) -> Dict[str, Any]:
        """
        获取我的排名
        
        Args:
            slug: 锦标赛 slug 或 ID
        """
        return self._request("GET", f"/{slug}/me/rank")
    
    def get_top3(self, slug: str) -> Dict[str, Any]:
        """
        获取 Top 3 英雄区数据
        
        Args:
            slug: 锦标赛 slug 或 ID
        """
        return self._request("GET", f"/{slug}/top3", auth_required=False)
