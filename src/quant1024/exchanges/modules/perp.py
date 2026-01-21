"""
PerpModule - 永续合约模块

实现 /api/v1/perp/ 下的所有 API 接口，包括：
- 市场数据 (Market Data)
- 交易 (Trading)
- 持仓 (Positions)
- 历史数据 (History)
- 高级订单 (Advanced Orders)

实现接口: IMarketData, ITrading, IPositions, IAdvancedOrders
"""

from typing import Any, Dict, List, Optional
from ._base import ModuleBase


class PerpModule(ModuleBase):
    """
    永续合约模块
    
    提供永续合约交易相关的所有 API 接口。
    
    Example:
        >>> exchange = Exchange1024ex(api_key="xxx", secret_key="xxx")
        >>> exchange.perp.get_ticker("BTC-USDC")
        >>> exchange.perp.place_order(market="BTC-USDC", side="long", order_type="limit", size="0.1", price="50000")
    """
    
    PATH_PREFIX = "/api/v1/perp"
    
    # ========== 市场数据 (Market Data) ==========
    
    def get_markets(self) -> List[Dict[str, Any]]:
        """获取所有永续合约市场"""
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
        params = {"limit": limit}
        result = self._request("GET", f"/markets/{market}/trades", params=params, auth_required=False)
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
        params: Dict[str, Any] = {"interval": interval, "limit": limit}
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        result = self._request("GET", f"/markets/{market}/klines", params=params, auth_required=False)
        return self._extract_data(result)
    
    def get_funding_rate(self, market: str) -> Dict[str, Any]:
        """获取当前资金费率"""
        return self._request("GET", f"/markets/{market}/funding-rate", auth_required=False)
    
    def get_funding_history(
        self,
        market: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取资金费率历史"""
        params: Dict[str, Any] = {"limit": limit}
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        result = self._request("GET", f"/markets/{market}/funding-history", params=params, auth_required=False)
        return self._extract_data(result)
    
    def get_mark_price(self, market: str) -> Dict[str, Any]:
        """获取标记价格"""
        return self._request("GET", f"/markets/{market}/mark-price", auth_required=False)
    
    def get_index_price(self, market: str) -> Dict[str, Any]:
        """获取指数价格"""
        return self._request("GET", f"/markets/{market}/index-price", auth_required=False)
    
    def get_open_interest(self, market: str) -> Dict[str, Any]:
        """获取持仓量"""
        return self._request("GET", f"/markets/{market}/open-interest", auth_required=False)
    
    def get_insurance_fund(self) -> Dict[str, Any]:
        """获取保险基金信息"""
        return self._request("GET", "/markets/insurance-fund", auth_required=False)
    
    # ========== 交易 (Trading) ==========
    
    def place_order(
        self,
        market: str,
        side: str,
        order_type: str,
        size: str,
        price: Optional[str] = None,
        leverage: Optional[int] = None,
        reduce_only: bool = False,
        post_only: bool = False,
        time_in_force: str = "GTC",
        client_order_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        下单
        
        Args:
            market: 市场名称 (如 BTC-USDC)
            side: 方向 (long/short)
            order_type: 订单类型 (limit/market)
            size: 数量
            price: 价格 (限价单必填)
            leverage: 杠杆倍数
            reduce_only: 只减仓
            post_only: 只做 Maker
            time_in_force: 有效期 (GTC/IOC/FOK)
            client_order_id: 客户端订单 ID
        """
        data: Dict[str, Any] = {
            "market": market,
            "side": side,
            "type": order_type,
            "size": size,
            "reduce_only": reduce_only,
            "post_only": post_only,
            "time_in_force": time_in_force
        }
        if price:
            data["price"] = price
        if leverage:
            data["leverage"] = leverage
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
    
    def get_orders(
        self,
        market: Optional[str] = None,
        side: Optional[str] = None,
        limit: int = 100,
        cursor: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取当前订单"""
        params: Dict[str, Any] = {"limit": limit}
        if market:
            params["market"] = market
        if side:
            params["side"] = side
        if cursor:
            params["cursor"] = cursor
        result = self._request("GET", "/orders", params=params)
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
    
    # ========== 持仓 (Positions) ==========
    
    def get_positions(self, market: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取所有持仓"""
        result = self._request("GET", "/positions")
        return self._extract_data(result)
    
    def get_position(self, market: str) -> Dict[str, Any]:
        """获取单个市场持仓"""
        return self._request("GET", f"/positions/{market}")
    
    def close_position(
        self,
        market: str,
        size: Optional[str] = None,
        price: Optional[str] = None,
        order_type: str = "market"
    ) -> Dict[str, Any]:
        """平仓"""
        data: Dict[str, Any] = {"type": order_type}
        if size:
            data["size"] = size
        if price:
            data["price"] = price
        return self._request("POST", f"/positions/{market}/close", data=data)
    
    def get_leverage(self, market: str) -> Dict[str, Any]:
        """获取杠杆设置"""
        return self._request("GET", f"/positions/{market}/leverage")
    
    def set_leverage(self, market: str, leverage: int) -> Dict[str, Any]:
        """设置杠杆"""
        data = {"leverage": leverage}
        return self._request("PUT", f"/positions/{market}/leverage", data=data)
    
    def adjust_margin(self, market: str, amount: str, adjust_type: str = "add") -> Dict[str, Any]:
        """调整保证金"""
        data = {"amount": amount, "type": adjust_type}
        return self._request("POST", f"/positions/{market}/margin", data=data)
    
    def set_tpsl(
        self,
        market: str,
        take_profit_price: Optional[str] = None,
        stop_loss_price: Optional[str] = None,
        take_profit_type: str = "market",
        stop_loss_type: str = "market"
    ) -> Dict[str, Any]:
        """设置止盈止损"""
        data: Dict[str, Any] = {
            "take_profit_type": take_profit_type,
            "stop_loss_type": stop_loss_type
        }
        if take_profit_price:
            data["take_profit_price"] = take_profit_price
        if stop_loss_price:
            data["stop_loss_price"] = stop_loss_price
        return self._request("POST", f"/positions/{market}/tpsl", data=data)
    
    def modify_tpsl(
        self,
        market: str,
        take_profit_price: Optional[str] = None,
        stop_loss_price: Optional[str] = None
    ) -> Dict[str, Any]:
        """修改止盈止损"""
        data: Dict[str, Any] = {}
        if take_profit_price:
            data["take_profit_price"] = take_profit_price
        if stop_loss_price:
            data["stop_loss_price"] = stop_loss_price
        return self._request("PUT", f"/positions/{market}/tpsl", data=data)
    
    def cancel_tpsl(self, market: str, tpsl_type: Optional[str] = None) -> Dict[str, Any]:
        """取消止盈止损"""
        params = {}
        if tpsl_type:
            params["type"] = tpsl_type
        return self._request("DELETE", f"/positions/{market}/tpsl", params=params)
    
    # ========== 历史数据 (History) ==========
    
    def get_order_history(
        self,
        market: Optional[str] = None,
        side: Optional[str] = None,
        status: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 100,
        cursor: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取历史订单"""
        params: Dict[str, Any] = {"limit": limit}
        if market:
            params["market"] = market
        if side:
            params["side"] = side
        if status:
            params["status"] = status
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        if cursor:
            params["cursor"] = cursor
        result = self._request("GET", "/orders/history", params=params)
        return self._extract_data(result)
    
    def get_trade_history(
        self,
        market: Optional[str] = None,
        order_id: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 100,
        cursor: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取成交历史"""
        params: Dict[str, Any] = {"limit": limit}
        if market:
            params["market"] = market
        if order_id:
            params["order_id"] = order_id
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        if cursor:
            params["cursor"] = cursor
        result = self._request("GET", "/trades", params=params)
        return self._extract_data(result)
    
    def get_user_funding_history(
        self,
        market: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取用户资金费历史"""
        params: Dict[str, Any] = {"limit": limit}
        if market:
            params["market"] = market
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        result = self._request("GET", "/funding/history", params=params)
        return self._extract_data(result)
    
    def get_liquidation_history(self) -> List[Dict[str, Any]]:
        """获取强平历史"""
        result = self._request("GET", "/liquidations")
        return self._extract_data(result)
    
    def get_pnl_summary(
        self,
        market: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取盈亏汇总"""
        params: Dict[str, Any] = {}
        if market:
            params["market"] = market
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        return self._request("GET", "/pnl", params=params)
    
    # ========== 高级订单 - TWAP ==========
    
    def create_twap(
        self,
        market: str,
        side: str,
        total_size: str,
        duration_seconds: int,
        interval_seconds: Optional[int] = None,
        slippage_tolerance: Optional[float] = None,
        reduce_only: bool = False,
        leverage: Optional[int] = None
    ) -> Dict[str, Any]:
        """创建 TWAP 订单"""
        data: Dict[str, Any] = {
            "market": market,
            "side": side,
            "total_size": total_size,
            "duration_seconds": duration_seconds,
            "reduce_only": reduce_only
        }
        if interval_seconds:
            data["interval_seconds"] = interval_seconds
        if slippage_tolerance:
            data["slippage_tolerance"] = slippage_tolerance
        if leverage:
            data["leverage"] = leverage
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
        slippage_tolerance: Optional[float] = None,
        reduce_only: bool = False,
        leverage: Optional[int] = None
    ) -> Dict[str, Any]:
        """创建 VWAP 订单"""
        data: Dict[str, Any] = {
            "market": market,
            "side": side,
            "total_size": total_size,
            "end_time": end_time,
            "reduce_only": reduce_only
        }
        if start_time:
            data["start_time"] = start_time
        if slippage_tolerance:
            data["slippage_tolerance"] = slippage_tolerance
        if leverage:
            data["leverage"] = leverage
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
        tp_trigger_price: str,
        sl_trigger_price: str,
        size: Optional[str] = None,
        tp_limit_price: Optional[str] = None,
        sl_limit_price: Optional[str] = None,
        reduce_only: bool = False,
        leverage: Optional[int] = None
    ) -> Dict[str, Any]:
        """创建 OCO 订单"""
        data: Dict[str, Any] = {
            "market": market,
            "side": side,
            "tp_trigger_price": tp_trigger_price,
            "sl_trigger_price": sl_trigger_price,
            "reduce_only": reduce_only
        }
        if size:
            data["size"] = size
        if tp_limit_price:
            data["tp_limit_price"] = tp_limit_price
        if sl_limit_price:
            data["sl_limit_price"] = sl_limit_price
        if leverage:
            data["leverage"] = leverage
        return self._request("POST", "/orders/oco", data=data)
    
    def get_oco_orders(self) -> List[Dict[str, Any]]:
        """获取 OCO 订单列表"""
        result = self._request("GET", "/orders/oco")
        return self._extract_data(result)
    
    def cancel_oco(self, order_id: str) -> Dict[str, Any]:
        """取消 OCO 订单"""
        return self._request("DELETE", f"/orders/oco/{order_id}")
    
    # ========== 高级订单 - Bracket ==========
    
    def create_bracket(
        self,
        market: str,
        side: str,
        size: str,
        take_profit_price: str,
        stop_loss_price: str,
        entry_price: Optional[str] = None,
        entry_type: str = "market",
        leverage: Optional[int] = None
    ) -> Dict[str, Any]:
        """创建 Bracket 订单"""
        data: Dict[str, Any] = {
            "market": market,
            "side": side,
            "size": size,
            "take_profit_price": take_profit_price,
            "stop_loss_price": stop_loss_price,
            "entry_type": entry_type
        }
        if entry_price:
            data["entry_price"] = entry_price
        if leverage:
            data["leverage"] = leverage
        return self._request("POST", "/orders/bracket", data=data)
    
    def get_bracket_orders(self) -> List[Dict[str, Any]]:
        """获取 Bracket 订单列表"""
        result = self._request("GET", "/orders/bracket")
        return self._extract_data(result)
    
    def cancel_bracket(self, order_id: str) -> Dict[str, Any]:
        """取消 Bracket 订单"""
        return self._request("DELETE", f"/orders/bracket/{order_id}")
    
    # ========== 高级订单 - Iceberg ==========
    
    def create_iceberg(
        self,
        market: str,
        side: str,
        total_size: str,
        visible_size: str,
        price: str,
        post_only: bool = False,
        reduce_only: bool = False,
        leverage: Optional[int] = None
    ) -> Dict[str, Any]:
        """创建冰山订单"""
        data: Dict[str, Any] = {
            "market": market,
            "side": side,
            "total_size": total_size,
            "visible_size": visible_size,
            "price": price,
            "post_only": post_only,
            "reduce_only": reduce_only
        }
        if leverage:
            data["leverage"] = leverage
        return self._request("POST", "/orders/iceberg", data=data)
    
    def get_iceberg_orders(self) -> List[Dict[str, Any]]:
        """获取冰山订单列表"""
        result = self._request("GET", "/orders/iceberg")
        return self._extract_data(result)
    
    def cancel_iceberg(self, order_id: str) -> Dict[str, Any]:
        """取消冰山订单"""
        return self._request("DELETE", f"/orders/iceberg/{order_id}")
    
    # ========== 高级订单 - Conditional ==========
    
    def create_conditional(
        self,
        market: str,
        side: str,
        size: str,
        trigger_price: str,
        order_type: str = "stop_market",
        limit_price: Optional[str] = None,
        trigger_price_type: str = "mark",
        slippage_tolerance: Optional[float] = None,
        reduce_only: bool = False,
        leverage: Optional[int] = None
    ) -> Dict[str, Any]:
        """创建条件订单"""
        data: Dict[str, Any] = {
            "market": market,
            "side": side,
            "size": size,
            "trigger_price": trigger_price,
            "order_type": order_type,
            "trigger_price_type": trigger_price_type,
            "reduce_only": reduce_only
        }
        if limit_price:
            data["limit_price"] = limit_price
        if slippage_tolerance:
            data["slippage_tolerance"] = slippage_tolerance
        if leverage:
            data["leverage"] = leverage
        return self._request("POST", "/orders/conditional", data=data)
    
    def get_conditional_orders(self) -> List[Dict[str, Any]]:
        """获取条件订单列表"""
        result = self._request("GET", "/orders/conditional")
        return self._extract_data(result)
    
    def cancel_conditional(self, order_id: str) -> Dict[str, Any]:
        """取消条件订单"""
        return self._request("DELETE", f"/orders/conditional/{order_id}")
    
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
        post_only: bool = False,
        reduce_only: bool = False,
        leverage: Optional[int] = None
    ) -> Dict[str, Any]:
        """创建阶梯订单"""
        data: Dict[str, Any] = {
            "market": market,
            "side": side,
            "total_size": total_size,
            "num_orders": num_orders,
            "start_price": start_price,
            "end_price": end_price,
            "post_only": post_only,
            "reduce_only": reduce_only
        }
        if size_skew:
            data["size_skew"] = size_skew
        if leverage:
            data["leverage"] = leverage
        return self._request("POST", "/orders/scale", data=data)
    
    def get_scale_orders(self) -> List[Dict[str, Any]]:
        """获取阶梯订单列表"""
        result = self._request("GET", "/orders/scale")
        return self._extract_data(result)
    
    def cancel_scale(self, order_id: str) -> Dict[str, Any]:
        """取消阶梯订单"""
        return self._request("DELETE", f"/orders/scale/{order_id}")
    
    # ========== 高级订单 - Trailing Stop ==========
    
    def create_trailing_stop(
        self,
        market: str,
        side: str,
        size: str,
        callback_rate: float,
        activation_price: Optional[str] = None,
        trigger_price_type: str = "mark",
        reduce_only: bool = True,
        leverage: Optional[int] = None
    ) -> Dict[str, Any]:
        """创建追踪止损订单"""
        data: Dict[str, Any] = {
            "market": market,
            "side": side,
            "size": size,
            "callback_rate": callback_rate,
            "trigger_price_type": trigger_price_type,
            "reduce_only": reduce_only
        }
        if activation_price:
            data["activation_price"] = activation_price
        if leverage:
            data["leverage"] = leverage
        return self._request("POST", "/orders/trailing-stop", data=data)
    
    def get_trailing_stop_orders(self) -> List[Dict[str, Any]]:
        """获取追踪止损订单列表"""
        result = self._request("GET", "/orders/trailing-stop")
        return self._extract_data(result)
    
    def cancel_trailing_stop(self, order_id: str) -> Dict[str, Any]:
        """取消追踪止损订单"""
        return self._request("DELETE", f"/orders/trailing-stop/{order_id}")
    
    # ========== 高级订单 - Pegged ==========
    
    def create_pegged(
        self,
        market: str,
        side: str,
        size: str,
        peg_type: str,
        offset: str,
        min_price: Optional[str] = None,
        max_price: Optional[str] = None,
        post_only: bool = False,
        reduce_only: bool = False,
        leverage: Optional[int] = None
    ) -> Dict[str, Any]:
        """创建 Pegged 订单"""
        data: Dict[str, Any] = {
            "market": market,
            "side": side,
            "size": size,
            "peg_type": peg_type,
            "offset": offset,
            "post_only": post_only,
            "reduce_only": reduce_only
        }
        if min_price:
            data["min_price"] = min_price
        if max_price:
            data["max_price"] = max_price
        if leverage:
            data["leverage"] = leverage
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
        max_duration_seconds: int,
        min_slice_size: Optional[str] = None,
        max_slice_size: Optional[str] = None,
        price_limit: Optional[str] = None,
        reduce_only: bool = False,
        leverage: Optional[int] = None
    ) -> Dict[str, Any]:
        """创建 POV 订单"""
        data: Dict[str, Any] = {
            "market": market,
            "side": side,
            "total_size": total_size,
            "participation_rate": participation_rate,
            "max_duration_seconds": max_duration_seconds,
            "reduce_only": reduce_only
        }
        if min_slice_size:
            data["min_slice_size"] = min_slice_size
        if max_slice_size:
            data["max_slice_size"] = max_slice_size
        if price_limit:
            data["price_limit"] = price_limit
        if leverage:
            data["leverage"] = leverage
        return self._request("POST", "/orders/pov", data=data)
    
    def get_pov_orders(self) -> List[Dict[str, Any]]:
        """获取 POV 订单列表"""
        result = self._request("GET", "/orders/pov")
        return self._extract_data(result)
    
    def cancel_pov(self, order_id: str) -> Dict[str, Any]:
        """取消 POV 订单"""
        return self._request("DELETE", f"/orders/pov/{order_id}")
    
    # ========== 高级订单 - Sniper ==========
    
    def create_sniper(
        self,
        market: str,
        side: str,
        size: str,
        sniper_type: str = "depth_trigger",
        target_price: Optional[str] = None,
        min_depth_qty: Optional[str] = None,
        slippage_tolerance: Optional[float] = None,
        max_wait_seconds: Optional[int] = None,
        reduce_only: bool = False,
        leverage: Optional[int] = None
    ) -> Dict[str, Any]:
        """创建狙击订单"""
        data: Dict[str, Any] = {
            "market": market,
            "side": side,
            "size": size,
            "sniper_type": sniper_type,
            "reduce_only": reduce_only
        }
        if target_price:
            data["target_price"] = target_price
        if min_depth_qty:
            data["min_depth_qty"] = min_depth_qty
        if slippage_tolerance:
            data["slippage_tolerance"] = slippage_tolerance
        if max_wait_seconds:
            data["max_wait_seconds"] = max_wait_seconds
        if leverage:
            data["leverage"] = leverage
        return self._request("POST", "/orders/sniper", data=data)
    
    def get_sniper_orders(self) -> List[Dict[str, Any]]:
        """获取狙击订单列表"""
        result = self._request("GET", "/orders/sniper")
        return self._extract_data(result)
    
    def cancel_sniper(self, order_id: str) -> Dict[str, Any]:
        """取消狙击订单"""
        return self._request("DELETE", f"/orders/sniper/{order_id}")
