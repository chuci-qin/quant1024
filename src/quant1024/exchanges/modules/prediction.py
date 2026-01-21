"""
PredictionModule - 预测市场模块

实现 /api/v1/prediction/ 下的所有 API 接口，包括：
- 市场发现 (Discovery)
- 市场详情 (Markets)
- 交易 (Trading)
- 用户数据 (User)
- Oracle 相关 (Oracle)

实现接口: IMarketData, ITrading
"""

from typing import Any, Dict, List, Optional
from ._base import ModuleBase


class PredictionModule(ModuleBase):
    """
    预测市场模块
    
    提供预测市场交易相关的所有 API 接口。
    
    Example:
        >>> exchange = Exchange1024ex(api_key="xxx", secret_key="xxx")
        >>> exchange.prediction.list_markets(category="crypto")
        >>> exchange.prediction.mint(market_id=123, amount=100_000_000)
    """
    
    PATH_PREFIX = "/api/v1/prediction"
    
    # ========== 市场发现 (Discovery) ==========
    
    def list_markets(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        market_type: Optional[str] = None,
        creator: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """获取市场列表"""
        params: Dict[str, Any] = {"page": page, "page_size": page_size}
        if status:
            params["status"] = status
        if category:
            params["category"] = category
        if market_type:
            params["market_type"] = market_type
        if creator:
            params["creator"] = creator
        return self._request("GET", "/markets", params=params, auth_required=False)
    
    def list_active_markets(self, limit: int = 50) -> Dict[str, Any]:
        """获取活跃市场"""
        params = {"limit": limit}
        return self._request("GET", "/markets/active", params=params, auth_required=False)
    
    def list_trending_markets(self, limit: int = 50) -> Dict[str, Any]:
        """获取热门市场 (按交易量)"""
        params = {"limit": limit}
        return self._request("GET", "/markets/trending", params=params, auth_required=False)
    
    def list_new_markets(self, limit: int = 50) -> Dict[str, Any]:
        """获取新市场"""
        params = {"limit": limit}
        return self._request("GET", "/markets/new", params=params, auth_required=False)
    
    def list_ending_soon_markets(self, limit: int = 50) -> Dict[str, Any]:
        """获取即将结束的市场"""
        params = {"limit": limit}
        return self._request("GET", "/markets/ending-soon", params=params, auth_required=False)
    
    def search_markets(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """搜索市场"""
        params = {"q": query, "limit": limit}
        return self._request("GET", "/search", params=params, auth_required=False)
    
    def list_categories(self) -> Dict[str, Any]:
        """获取分类列表"""
        return self._request("GET", "/categories", auth_required=False)
    
    def list_tags(self, limit: int = 50) -> Dict[str, Any]:
        """获取热门标签"""
        params = {"limit": limit}
        return self._request("GET", "/tags", params=params, auth_required=False)
    
    # ========== 市场详情 (Markets) ==========
    
    def get_market(self, market_id: str) -> Dict[str, Any]:
        """获取市场详情"""
        return self._request("GET", f"/markets/{market_id}", auth_required=False)
    
    def get_market_stats(self, market_id: str) -> Dict[str, Any]:
        """获取市场统计"""
        return self._request("GET", f"/markets/{market_id}/stats", auth_required=False)
    
    def get_market_outcomes(self, market_id: str) -> Dict[str, Any]:
        """获取市场结果选项 (多结果市场)"""
        return self._request("GET", f"/markets/{market_id}/outcomes", auth_required=False)
    
    def get_market_orderbook(self, market_id: str) -> Dict[str, Any]:
        """获取市场订单簿"""
        return self._request("GET", f"/markets/{market_id}/orderbook", auth_required=False)
    
    def get_market_depth(self, market_id: str, outcome_index: int = 0) -> Dict[str, Any]:
        """获取市场深度"""
        params = {"outcome_index": outcome_index}
        return self._request("GET", f"/markets/{market_id}/depth", params=params, auth_required=False)
    
    def get_all_depths(self, market_id: str) -> Dict[str, Any]:
        """获取所有结果的深度"""
        return self._request("GET", f"/markets/{market_id}/all-depths", auth_required=False)
    
    def get_market_trades(self, market_id: str, limit: int = 50) -> Dict[str, Any]:
        """获取市场成交"""
        params = {"limit": limit}
        return self._request("GET", f"/markets/{market_id}/trades", params=params, auth_required=False)
    
    def get_market_orders(self, market_id: str, limit: int = 50) -> Dict[str, Any]:
        """获取市场订单"""
        params = {"limit": limit}
        return self._request("GET", f"/markets/{market_id}/orders", params=params, auth_required=False)
    
    def get_price_history(
        self,
        market_id: str,
        outcome_index: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """获取价格历史"""
        params = {"outcome_index": outcome_index, "limit": limit}
        return self._request("GET", f"/markets/{market_id}/price-history", params=params, auth_required=False)
    
    def get_klines(
        self,
        market_id: str,
        outcome_index: int = 0,
        interval: str = "1h",
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """获取 K 线数据"""
        params: Dict[str, Any] = {
            "outcome_index": outcome_index,
            "interval": interval,
            "limit": limit
        }
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        return self._request("GET", f"/markets/{market_id}/klines", params=params, auth_required=False)
    
    def get_price_balance(self, market_id: str) -> Dict[str, Any]:
        """获取价格平衡 (CTF 约束检查)"""
        return self._request("GET", f"/markets/{market_id}/price-balance", auth_required=False)
    
    def batch_get_prices(self, market_ids: List[int]) -> Dict[str, Any]:
        """批量获取市场价格"""
        data = {"market_ids": market_ids}
        return self._request("POST", "/markets/batch-prices", data=data, auth_required=False)
    
    # ========== 交易 (Trading) - 二元市场 ==========
    
    def mint(self, market_id: int, amount: int) -> Dict[str, Any]:
        """
        铸造完整集 (存入 USDC，获得 Yes+No 代币)
        
        Args:
            market_id: 市场 ID
            amount: USDC 数量 (6 位小数)
        """
        data = {"market_id": market_id, "amount": amount}
        return self._request("POST", "/mints", data=data)
    
    def redeem(self, market_id: int, amount: int) -> Dict[str, Any]:
        """
        赎回完整集 (销毁 Yes+No 代币，取回 USDC)
        
        Args:
            market_id: 市场 ID
            amount: 代币数量
        """
        data = {"market_id": market_id, "amount": amount}
        return self._request("POST", "/redemptions", data=data)
    
    def claim(self, market_id: int) -> Dict[str, Any]:
        """
        领取收益 (市场结算后)
        
        Args:
            market_id: 市场 ID
        """
        data = {"market_id": market_id}
        return self._request("POST", "/claims", data=data)
    
    def place_order(
        self,
        market_id: int,
        side: int,
        outcome_index: int,
        price_e6: int,
        amount: int
    ) -> Dict[str, Any]:
        """
        下限价单
        
        Args:
            market_id: 市场 ID
            side: 0=买, 1=卖
            outcome_index: 结果索引 (0=Yes, 1=No)
            price_e6: 价格 (e6 格式，如 650000 = $0.65)
            amount: 份额数量
        """
        data = {
            "market_id": market_id,
            "side": side,
            "outcome_index": outcome_index,
            "price_e6": price_e6,
            "amount": amount
        }
        return self._request("POST", "/orders", data=data)
    
    def cancel_order(self, market_id: int, order_id: int) -> Dict[str, Any]:
        """取消订单"""
        data = {"market_id": market_id, "order_id": order_id}
        return self._request("POST", "/orders/cancel", data=data)
    
    def cancel_all_orders(self, market_id: Optional[int] = None) -> Dict[str, Any]:
        """取消所有订单"""
        data: Dict[str, Any] = {}
        if market_id:
            data["market_id"] = market_id
        return self._request("POST", "/orders/cancel-all", data=data)
    
    def batch_cancel_orders(self, market_id: int, order_ids: List[int]) -> Dict[str, Any]:
        """批量取消订单"""
        data = {"market_id": market_id, "order_ids": order_ids}
        return self._request("POST", "/orders/batch-cancel", data=data)
    
    # ========== 交易 (Trading) - 多结果市场 ==========
    
    def multi_mint(self, market_id: int, amount: int) -> Dict[str, Any]:
        """多结果市场铸造"""
        data = {"market_id": market_id, "amount": amount}
        return self._request("POST", "/multi-outcome/mints", data=data)
    
    def multi_redeem(self, market_id: int, amount: int) -> Dict[str, Any]:
        """多结果市场赎回"""
        data = {"market_id": market_id, "amount": amount}
        return self._request("POST", "/multi-outcome/redemptions", data=data)
    
    def multi_claim(self, market_id: int, outcome_index: int) -> Dict[str, Any]:
        """多结果市场领取收益"""
        data = {"market_id": market_id, "outcome_index": outcome_index}
        return self._request("POST", "/multi-outcome/claims", data=data)
    
    def multi_place_order(
        self,
        market_id: int,
        side: int,
        outcome_index: int,
        price_e6: int,
        amount: int
    ) -> Dict[str, Any]:
        """多结果市场下单"""
        data = {
            "market_id": market_id,
            "side": side,
            "outcome_index": outcome_index,
            "price_e6": price_e6,
            "amount": amount
        }
        return self._request("POST", "/multi-outcome/orders", data=data)
    
    # ========== 用户数据 (User) ==========
    
    def get_my_positions(self) -> Dict[str, Any]:
        """获取我的持仓"""
        return self._request("GET", "/me/positions")
    
    def get_my_orders(
        self,
        market_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """获取我的订单"""
        params: Dict[str, Any] = {"limit": limit}
        if market_id:
            params["market_id"] = market_id
        if status:
            params["status"] = status
        return self._request("GET", "/me/orders", params=params)
    
    def get_my_trades(
        self,
        market_id: Optional[int] = None,
        limit: int = 50
    ) -> Dict[str, Any]:
        """获取我的成交"""
        params: Dict[str, Any] = {"limit": limit}
        if market_id:
            params["market_id"] = market_id
        return self._request("GET", "/me/trades", params=params)
    
    def get_my_matches(self, limit: int = 50) -> Dict[str, Any]:
        """获取我的撮合历史"""
        params = {"limit": limit}
        return self._request("GET", "/me/matches", params=params)
    
    def get_my_stats(self) -> Dict[str, Any]:
        """获取我的统计数据"""
        return self._request("GET", "/me/stats")
    
    def get_activity(self, limit: int = 50) -> Dict[str, Any]:
        """获取活动动态"""
        params = {"limit": limit}
        return self._request("GET", "/activity", params=params, auth_required=False)
    
    def get_global_matches(self, limit: int = 50) -> Dict[str, Any]:
        """获取全局撮合历史"""
        params = {"limit": limit}
        return self._request("GET", "/matches", params=params, auth_required=False)
    
    def get_market_match_stats(self, market_id: str) -> Dict[str, Any]:
        """获取市场撮合统计"""
        return self._request("GET", f"/markets/{market_id}/match-stats", auth_required=False)
    
    # ========== Oracle 相关 ==========
    
    def get_oracle_config(self, market_id: int) -> Dict[str, Any]:
        """获取 Oracle 配置"""
        return self._request("GET", f"/markets/{market_id}/oracle-config", auth_required=False)
    
    def get_proposal(self, market_id: int) -> Dict[str, Any]:
        """获取当前提案"""
        return self._request("GET", f"/markets/{market_id}/proposal", auth_required=False)
    
    def get_research(self, market_id: int) -> Dict[str, Any]:
        """获取 LLM Oracle 研究数据"""
        return self._request("GET", f"/markets/{market_id}/research", auth_required=False)
    
    def challenge_result(
        self,
        market_id: int,
        challenger_outcome_index: int,
        evidence_hash: Optional[str] = None
    ) -> Dict[str, Any]:
        """挑战结果"""
        data: Dict[str, Any] = {
            "market_id": market_id,
            "challenger_outcome_index": challenger_outcome_index
        }
        if evidence_hash:
            data["evidence_hash"] = evidence_hash
        return self._request("POST", "/oracle/challenges", data=data)
    
    def finalize_result(self, market_id: int) -> Dict[str, Any]:
        """确认结果 (挑战期结束后)"""
        data = {"market_id": market_id}
        return self._request("POST", "/oracle/finalizations", data=data)
