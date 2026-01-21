"""
SpotModule - 现货交易模块

实现 /api/v1/spot/ 下的所有 API 接口，包括：
- 市场数据 (Market Data)
- 交易 (Trading)
- 余额 (Balances)
- 历史数据 (History)
- 高级订单 (Advanced Orders)

实现接口: IMarketData, ITrading
"""

from typing import Any, Dict, List, Optional
from ._base import ModuleBase


class SpotModule(ModuleBase):
    """
    现货交易模块
    
    提供现货交易相关的所有 API 接口。
    
    Example:
        >>> exchange = Exchange1024ex(api_key="xxx", secret_key="xxx")
        >>> exchange.spot.get_balances()
        >>> exchange.spot.place_order(market="BTC/USDC", side="buy", order_type="limit", size="0.1", price="50000")
    """
    
    PATH_PREFIX = "/api/v1/spot"
    
    # ========== 市场数据 (Market Data) ==========
    
    def get_markets(self) -> List[Dict[str, Any]]:
        """获取所有现货市场"""
        result = self._request("GET", "/markets", auth_required=False)
        return self._extract_data(result)
    
    def get_market(self, market: str) -> Dict[str, Any]:
        """获取单个市场信息"""
        return self._request("GET", f"/markets/{market}", auth_required=False)
    
    def get_ticker(self, market: str) -> Dict[str, Any]:
        """获取 24h 行情"""
        return self._request("GET", f"/markets/{market}/ticker", auth_required=False)
    
    def get_orderbook(self, market: str, depth: int = 20) -> Dict[str, Any]:
        """获取订单簿"""
        params = {"depth": depth}
        return self._request("GET", f"/markets/{market}/orderbook", params=params, auth_required=False)
    
    def get_trades(self, market: str, limit: int = 100) -> List[Dict[str, Any]]:
        """获取最近成交"""
        result = self._request("GET", f"/markets/{market}/trades", auth_required=False)
        return self._extract_data(result)
    
    def get_klines(
        self,
        market: str,
        interval: str = "1h",
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 500
    ) -> List[Dict[str, Any]]:
        """获取 K 线数据"""
        result = self._request("GET", f"/markets/{market}/klines", auth_required=False)
        return self._extract_data(result)
    
    def get_tokens(self) -> List[Dict[str, Any]]:
        """获取所有代币信息"""
        result = self._request("GET", "/tokens", auth_required=False)
        return self._extract_data(result)
    
    def get_token(self, symbol: str) -> Dict[str, Any]:
        """获取单个代币信息"""
        return self._request("GET", f"/tokens/{symbol}", auth_required=False)
    
    # ========== 余额 (Balances) ==========
    
    def get_balances(self) -> Dict[str, Any]:
        """获取所有代币余额"""
        return self._request("GET", "/balances")
    
    def get_balance(self, symbol: str) -> Dict[str, Any]:
        """获取单个代币余额"""
        return self._request("GET", f"/balances/{symbol}")
    
    # ========== 交易 (Trading) ==========
    
    def place_order(
        self,
        market: str,
        side: str,
        order_type: str,
        size: str,
        price: Optional[str] = None,
        quote_amount: Optional[str] = None,
        post_only: bool = False,
        time_in_force: str = "GTC",
        client_order_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        下单
        
        Args:
            market: 市场名称 (如 BTC/USDC)
            side: 方向 (buy/sell)
            order_type: 订单类型 (limit/market)
            size: 数量 (基础货币)
            price: 价格 (限价单必填)
            quote_amount: 报价货币数量 (如 "买 100 USDC 的 BTC")
            post_only: 只做 Maker
            time_in_force: 有效期 (GTC/IOC/FOK)
            client_order_id: 客户端订单 ID
        """
        data: Dict[str, Any] = {
            "market": market,
            "side": side,
            "type": order_type,
            "size": size,
            "post_only": post_only,
            "time_in_force": time_in_force
        }
        if price:
            data["price"] = price
        if quote_amount:
            data["quote_amount"] = quote_amount
        if client_order_id:
            data["client_order_id"] = client_order_id
        
        return self._request("POST", "/orders", data=data)
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """撤销订单"""
        return self._request("DELETE", f"/orders/{order_id}")
    
    def cancel_all_orders(self, market: Optional[str] = None) -> Dict[str, Any]:
        """批量撤销订单"""
        params = {}
        if market:
            params["market"] = market
        return self._request("DELETE", "/orders", params=params)
    
    def get_orders(self, market: Optional[str] = None, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取当前订单"""
        result = self._request("GET", "/orders")
        return self._extract_data(result)
    
    def get_order(self, order_id: str) -> Dict[str, Any]:
        """获取订单详情"""
        return self._request("GET", f"/orders/{order_id}")
    
    def update_order(
        self,
        order_id: str,
        price: str,
        size: Optional[str] = None
    ) -> Dict[str, Any]:
        """修改订单"""
        data: Dict[str, Any] = {"price": price}
        if size:
            data["size"] = size
        return self._request("PUT", f"/orders/{order_id}", data=data)
    
    def batch_place_orders(self, orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量下单"""
        data = {"orders": orders}
        return self._request("POST", "/orders/batch", data=data)
    
    def batch_cancel_orders(self, order_ids: List[str]) -> Dict[str, Any]:
        """批量撤单"""
        data = {"order_ids": order_ids}
        return self._request("DELETE", "/orders/batch", data=data)
    
    # ========== 历史数据 (History) ==========
    
    def get_order_history(
        self,
        market: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取历史订单"""
        result = self._request("GET", "/orders/history")
        return self._extract_data(result)
    
    def get_trade_history(
        self,
        market: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取成交历史"""
        result = self._request("GET", "/trades")
        return self._extract_data(result)
    
    # ========== 高级订单 - Conditional ==========
    
    def create_conditional(
        self,
        market: str,
        side: str,
        size: str,
        trigger_price: str,
        order_type: str = "stop_market",
        limit_price: Optional[str] = None,
        trigger_price_type: str = "last"
    ) -> Dict[str, Any]:
        """创建条件订单"""
        data: Dict[str, Any] = {
            "market": market,
            "side": side,
            "size": size,
            "trigger_price": trigger_price,
            "order_type": order_type,
            "trigger_price_type": trigger_price_type
        }
        if limit_price:
            data["limit_price"] = limit_price
        return self._request("POST", "/orders/conditional", data=data)
    
    def get_conditional_orders(self) -> List[Dict[str, Any]]:
        """获取条件订单列表"""
        result = self._request("GET", "/orders/conditional")
        return self._extract_data(result)
    
    def cancel_conditional(self, order_id: str) -> Dict[str, Any]:
        """取消条件订单"""
        return self._request("DELETE", f"/orders/conditional/{order_id}")
    
    # ========== 高级订单 - TWAP ==========
    
    def create_twap(
        self,
        market: str,
        side: str,
        total_size: str,
        duration_seconds: int,
        interval_seconds: Optional[int] = None,
        slippage_tolerance: Optional[float] = None
    ) -> Dict[str, Any]:
        """创建 TWAP 订单"""
        data: Dict[str, Any] = {
            "market": market,
            "side": side,
            "total_size": total_size,
            "duration_seconds": duration_seconds
        }
        if interval_seconds:
            data["interval_seconds"] = interval_seconds
        if slippage_tolerance:
            data["slippage_tolerance"] = slippage_tolerance
        return self._request("POST", "/orders/twap", data=data)
    
    def get_twap_orders(self) -> List[Dict[str, Any]]:
        """获取 TWAP 订单列表"""
        result = self._request("GET", "/orders/twap")
        return self._extract_data(result)
    
    def cancel_twap(self, order_id: str) -> Dict[str, Any]:
        """取消 TWAP 订单"""
        return self._request("DELETE", f"/orders/twap/{order_id}")
    
    # ========== 高级订单 - VWAP ==========
    
    def create_vwap(
        self,
        market: str,
        side: str,
        total_size: str,
        end_time: int,
        start_time: Optional[int] = None,
        slippage_tolerance: Optional[float] = None
    ) -> Dict[str, Any]:
        """创建 VWAP 订单"""
        data: Dict[str, Any] = {
            "market": market,
            "side": side,
            "total_size": total_size,
            "end_time": end_time
        }
        if start_time:
            data["start_time"] = start_time
        if slippage_tolerance:
            data["slippage_tolerance"] = slippage_tolerance
        return self._request("POST", "/orders/vwap", data=data)
    
    def get_vwap_orders(self) -> List[Dict[str, Any]]:
        """获取 VWAP 订单列表"""
        result = self._request("GET", "/orders/vwap")
        return self._extract_data(result)
    
    def cancel_vwap(self, order_id: str) -> Dict[str, Any]:
        """取消 VWAP 订单"""
        return self._request("DELETE", f"/orders/vwap/{order_id}")
    
    # ========== 高级订单 - OCO ==========
    
    def create_oco(
        self,
        market: str,
        side: str,
        size: str,
        limit_price: str,
        stop_price: str,
        stop_limit_price: Optional[str] = None
    ) -> Dict[str, Any]:
        """创建 OCO 订单"""
        data: Dict[str, Any] = {
            "market": market,
            "side": side,
            "size": size,
            "limit_price": limit_price,
            "stop_price": stop_price
        }
        if stop_limit_price:
            data["stop_limit_price"] = stop_limit_price
        return self._request("POST", "/orders/oco", data=data)
    
    def get_oco_orders(self) -> List[Dict[str, Any]]:
        """获取 OCO 订单列表"""
        result = self._request("GET", "/orders/oco")
        return self._extract_data(result)
    
    def cancel_oco(self, order_id: str) -> Dict[str, Any]:
        """取消 OCO 订单"""
        return self._request("DELETE", f"/orders/oco/{order_id}")
    
    # ========== 高级订单 - Iceberg ==========
    
    def create_iceberg(
        self,
        market: str,
        side: str,
        total_size: str,
        visible_size: str,
        price: str,
        post_only: bool = False
    ) -> Dict[str, Any]:
        """创建冰山订单"""
        data: Dict[str, Any] = {
            "market": market,
            "side": side,
            "total_size": total_size,
            "visible_size": visible_size,
            "price": price,
            "post_only": post_only
        }
        return self._request("POST", "/orders/iceberg", data=data)
    
    def get_iceberg_orders(self) -> List[Dict[str, Any]]:
        """获取冰山订单列表"""
        result = self._request("GET", "/orders/iceberg")
        return self._extract_data(result)
    
    def cancel_iceberg(self, order_id: str) -> Dict[str, Any]:
        """取消冰山订单"""
        return self._request("DELETE", f"/orders/iceberg/{order_id}")
    
    # ========== 高级订单 - Scale ==========
    
    def create_scale(
        self,
        market: str,
        side: str,
        total_size: str,
        num_orders: int,
        start_price: str,
        end_price: str,
        size_skew: Optional[float] = None,
        post_only: bool = False
    ) -> Dict[str, Any]:
        """创建阶梯订单"""
        data: Dict[str, Any] = {
            "market": market,
            "side": side,
            "total_size": total_size,
            "num_orders": num_orders,
            "start_price": start_price,
            "end_price": end_price,
            "post_only": post_only
        }
        if size_skew:
            data["size_skew"] = size_skew
        return self._request("POST", "/orders/scale", data=data)
    
    def get_scale_orders(self) -> List[Dict[str, Any]]:
        """获取阶梯订单列表"""
        result = self._request("GET", "/orders/scale")
        return self._extract_data(result)
    
    def cancel_scale(self, order_id: str) -> Dict[str, Any]:
        """取消阶梯订单"""
        return self._request("DELETE", f"/orders/scale/{order_id}")
    
    # ========== 高级订单 - Pegged ==========
    
    def create_pegged(
        self,
        market: str,
        side: str,
        size: str,
        peg_type: str,
        offset: str,
        post_only: bool = False
    ) -> Dict[str, Any]:
        """创建 Pegged 订单"""
        data: Dict[str, Any] = {
            "market": market,
            "side": side,
            "size": size,
            "peg_type": peg_type,
            "offset": offset,
            "post_only": post_only
        }
        return self._request("POST", "/orders/pegged", data=data)
    
    def get_pegged_orders(self) -> List[Dict[str, Any]]:
        """获取 Pegged 订单列表"""
        result = self._request("GET", "/orders/pegged")
        return self._extract_data(result)
    
    def cancel_pegged(self, order_id: str) -> Dict[str, Any]:
        """取消 Pegged 订单"""
        return self._request("DELETE", f"/orders/pegged/{order_id}")
    
    # ========== 高级订单 - POV ==========
    
    def create_pov(
        self,
        market: str,
        side: str,
        total_size: str,
        participation_rate: float,
        max_duration_seconds: int
    ) -> Dict[str, Any]:
        """创建 POV 订单"""
        data: Dict[str, Any] = {
            "market": market,
            "side": side,
            "total_size": total_size,
            "participation_rate": participation_rate,
            "max_duration_seconds": max_duration_seconds
        }
        return self._request("POST", "/orders/pov", data=data)
    
    def get_pov_orders(self) -> List[Dict[str, Any]]:
        """获取 POV 订单列表"""
        result = self._request("GET", "/orders/pov")
        return self._extract_data(result)
    
    def cancel_pov(self, order_id: str) -> Dict[str, Any]:
        """取消 POV 订单"""
        return self._request("DELETE", f"/orders/pov/{order_id}")
