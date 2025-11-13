"""
1024ex Exchange connector
"""

import requests
import json
import time
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin

from .base import BaseExchange
from ..auth.hmac_auth import get_auth_headers
from ..exceptions import (
    APIError,
    AuthenticationError,
    RateLimitError,
    InvalidParameterError,
    OrderNotFoundError,
    MarketNotFoundError
)


class Exchange1024ex(BaseExchange):
    """
    1024 Exchange 连接器
    
    实现 1024ex Public API 的完整封装（38个端点）
    """
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        base_url: str = "https://api.1024ex.com",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        初始化 1024ex 客户端
        
        Args:
            api_key: API Key
            api_secret: API Secret
            base_url: API 基础 URL
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        super().__init__(api_key, api_secret, base_url)
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
    
    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        auth_required: bool = True
    ) -> Dict[str, Any]:
        """
        发送 HTTP 请求
        
        Args:
            method: HTTP 方法
            path: API 路径
            params: URL 参数
            data: 请求体数据
            auth_required: 是否需要认证
        
        Returns:
            API 响应数据
        
        Raises:
            APIError: API 错误
            AuthenticationError: 认证错误
            RateLimitError: 速率限制
        """
        url = urljoin(self.base_url, path)
        
        # 构造请求体
        body = ""
        if data:
            body = json.dumps(data)
        
        # 构造 Headers
        headers = {}
        if auth_required:
            headers = get_auth_headers(
                self.api_key,
                self.api_secret,
                method,
                path,
                body
            )
        else:
            headers = {"Content-Type": "application/json"}
        
        # 发送请求（带重试）
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    data=body if data else None,
                    timeout=self.timeout
                )
                
                # 处理 HTTP 错误
                if response.status_code == 401:
                    raise AuthenticationError("认证失败，请检查 API Key 和 Secret")
                elif response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    raise RateLimitError(f"速率限制，请等待 {retry_after} 秒")
                elif response.status_code == 404:
                    raise MarketNotFoundError("资源未找到")
                elif response.status_code >= 400:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('message', f'HTTP {response.status_code}')
                    except:
                        error_msg = f'HTTP {response.status_code}'
                    raise APIError(error_msg)
                
                # 解析响应
                try:
                    result = response.json()
                    return result
                except ValueError:
                    return {"success": True, "data": response.text}
            
            except (requests.ConnectionError, requests.Timeout) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                    continue
                else:
                    raise APIError(f"请求失败: {str(e)}")
            
            except RateLimitError:
                raise  # 速率限制不重试
            
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
        
        if last_exception:
            raise APIError(f"请求失败: {str(last_exception)}")
        
        return {}
    
    # ========== 系统接口（3个）==========
    
    def get_server_time(self) -> Dict[str, Any]:
        """
        获取服务器时间
        
        Returns:
            {
                "success": True,
                "data": {
                    "server_time": 1762911479265,
                    "timezone": "UTC"
                },
                "timestamp": 1762911479265
            }
        """
        return self._request("GET", "/api/v1/time", auth_required=False)
    
    def get_health(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            {"status": "ok", "services": {...}}
        """
        return self._request("GET", "/api/v1/health", auth_required=False)
    
    def get_exchange_info(self) -> Dict[str, Any]:
        """
        获取交易所信息
        
        Returns:
            交易所配置信息
        """
        return self._request("GET", "/api/v1/exchange-info", auth_required=False)
    
    # ========== 市场数据（8个）==========
    
    def get_markets(self) -> List[Dict[str, Any]]:
        """
        获取所有市场
        
        Returns:
            市场列表
        """
        result = self._request("GET", "/api/v1/markets", auth_required=False)
        return result.get('data', result) if isinstance(result, dict) else result
    
    def get_market(self, market: str) -> Dict[str, Any]:
        """
        获取单个市场信息
        
        Args:
            market: 市场名称，如 BTC-PERP
        
        Returns:
            市场信息
        """
        return self._request("GET", f"/api/v1/markets/{market}", auth_required=False)
    
    def get_ticker(self, market: str) -> Dict[str, Any]:
        """
        获取24小时行情
        
        Args:
            market: 市场名称
        
        Returns:
            行情数据
        """
        return self._request("GET", f"/api/v1/ticker/{market}", auth_required=False)
    
    def get_orderbook(self, market: str, depth: int = 20) -> Dict[str, Any]:
        """
        获取订单簿
        
        Args:
            market: 市场名称
            depth: 深度（默认20档）
        
        Returns:
            订单簿数据
        """
        params = {"depth": depth}
        return self._request("GET", f"/api/v1/orderbook/{market}", params=params, auth_required=False)
    
    def get_trades(self, market: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取最近成交
        
        Args:
            market: 市场名称
            limit: 数量限制
        
        Returns:
            成交列表
        """
        params = {"limit": limit}
        result = self._request("GET", f"/api/v1/trades/{market}", params=params, auth_required=False)
        return result.get('data', result) if isinstance(result, dict) else result
    
    def get_klines(
        self,
        market: str,
        interval: str = '1h',
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取K线数据
        
        Args:
            market: 市场名称
            interval: 时间间隔（1m, 5m, 15m, 1h, 4h, 1d）
            start_time: 开始时间（时间戳，毫秒）
            end_time: 结束时间（时间戳，毫秒）
            limit: 数量限制
        
        Returns:
            K线列表
        """
        params = {
            "interval": interval,
            "limit": limit
        }
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        
        result = self._request("GET", f"/api/v1/klines/{market}", params=params, auth_required=False)
        return result.get('data', result) if isinstance(result, dict) else result
    
    def get_funding_rate(self, market: str) -> Dict[str, Any]:
        """
        获取资金费率
        
        Args:
            market: 市场名称
        
        Returns:
            资金费率信息
        """
        return self._request("GET", f"/api/v1/funding-rate/{market}", auth_required=False)
    
    def get_market_stats(self, market: str) -> Dict[str, Any]:
        """
        获取市场统计
        
        Args:
            market: 市场名称
        
        Returns:
            市场统计数据
        """
        return self._request("GET", f"/api/v1/market-stats/{market}", auth_required=False)
    
    # ========== 交易接口（8个）==========
    
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
            market: 市场名称
            side: 方向（buy/sell）
            order_type: 订单类型（limit/market）
            size: 数量
            price: 价格（限价单必填）
            leverage: 杠杆倍数
            reduce_only: 只减仓
            post_only: 只做 Maker
            time_in_force: 有效期（GTC/IOC/FOK）
            client_order_id: 客户端订单ID
        
        Returns:
            订单信息
        """
        data = {
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
        
        return self._request("POST", "/api/v1/orders", data=data)
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        撤单
        
        Args:
            order_id: 订单ID
        
        Returns:
            撤单结果
        """
        return self._request("DELETE", f"/api/v1/orders/{order_id}")
    
    def cancel_all_orders(self, market: Optional[str] = None) -> Dict[str, Any]:
        """
        批量撤单
        
        Args:
            market: 市场名称（可选，不填则撤销所有）
        
        Returns:
            撤单结果
        """
        params = {}
        if market:
            params["market"] = market
        
        return self._request("DELETE", "/api/v1/orders", params=params)
    
    def get_orders(
        self,
        market: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取当前委托
        
        Args:
            market: 市场名称（可选）
            status: 订单状态（可选）
        
        Returns:
            订单列表
        """
        params = {}
        if market:
            params["market"] = market
        if status:
            params["status"] = status
        
        result = self._request("GET", "/api/v1/orders", params=params)
        return result.get('data', result) if isinstance(result, dict) else result
    
    def get_order(self, order_id: str) -> Dict[str, Any]:
        """
        获取订单详情
        
        Args:
            order_id: 订单ID
        
        Returns:
            订单详情
        """
        return self._request("GET", f"/api/v1/orders/{order_id}")
    
    def update_order(
        self,
        order_id: str,
        price: str,
        size: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        修改订单
        
        Args:
            order_id: 订单ID
            price: 新价格
            size: 新数量（可选）
        
        Returns:
            修改后的订单
        """
        data = {"price": price}
        if size:
            data["size"] = size
        
        return self._request("PUT", f"/api/v1/orders/{order_id}", data=data)
    
    def batch_place_orders(self, orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量下单
        
        Args:
            orders: 订单列表
        
        Returns:
            批量下单结果
        """
        data = {"orders": orders}
        return self._request("POST", "/api/v1/orders/batch", data=data)
    
    def set_tpsl(
        self,
        market: str,
        tp_price: Optional[str] = None,
        sl_price: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        设置止盈止损
        
        Args:
            market: 市场名称
            tp_price: 止盈价格
            sl_price: 止损价格
        
        Returns:
            设置结果
        """
        data = {}
        if tp_price:
            data["take_profit_price"] = tp_price
        if sl_price:
            data["stop_loss_price"] = sl_price
        
        return self._request("PUT", f"/api/v1/positions/{market}/tpsl", data=data)
    
    # ========== 账户接口（6个）==========
    
    def get_balance(self) -> Dict[str, Any]:
        """
        获取账户余额
        
        Returns:
            余额信息
        """
        return self._request("GET", "/api/v1/account/balance")
    
    def get_positions(self, market: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取持仓
        
        Args:
            market: 市场名称（可选）
        
        Returns:
            持仓列表
        """
        params = {}
        if market:
            params["market"] = market
        
        result = self._request("GET", "/api/v1/account/positions", params=params)
        return result.get('data', result) if isinstance(result, dict) else result
    
    def get_margin(self) -> Dict[str, Any]:
        """
        获取保证金信息
        
        Returns:
            保证金信息
        """
        return self._request("GET", "/api/v1/account/margin")
    
    def get_leverage(self, market: str) -> Dict[str, Any]:
        """
        查询杠杆
        
        Args:
            market: 市场名称
        
        Returns:
            杠杆信息
        """
        return self._request("GET", f"/api/v1/account/leverage/{market}")
    
    def set_leverage(self, market: str, leverage: int) -> Dict[str, Any]:
        """
        设置杠杆
        
        Args:
            market: 市场名称
            leverage: 杠杆倍数
        
        Returns:
            设置结果
        """
        data = {"leverage": leverage}
        return self._request("PUT", f"/api/v1/account/leverage/{market}", data=data)
    
    def get_sub_accounts(self) -> List[Dict[str, Any]]:
        """
        获取子账户列表
        
        Returns:
            子账户列表
        """
        result = self._request("GET", "/api/v1/account/sub-accounts")
        return result.get('data', result) if isinstance(result, dict) else result
    
    # ========== 资金接口（4个）==========
    
    def get_deposit_address(self, asset: str) -> Dict[str, Any]:
        """
        获取充值地址
        
        Args:
            asset: 资产名称（如 USDC）
        
        Returns:
            充值地址信息
        """
        data = {"asset": asset}
        return self._request("POST", "/api/v1/account/deposit", data=data)
    
    def withdraw(
        self,
        asset: str,
        amount: str,
        address: str,
        memo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        提现
        
        Args:
            asset: 资产名称
            amount: 提现数量
            address: 提现地址
            memo: 备注（可选）
        
        Returns:
            提现结果
        """
        data = {
            "asset": asset,
            "amount": amount,
            "address": address
        }
        if memo:
            data["memo"] = memo
        
        return self._request("POST", "/api/v1/account/withdraw", data=data)
    
    def get_deposit_history(
        self,
        asset: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        获取充值历史
        
        Args:
            asset: 资产名称（可选）
            limit: 数量限制
        
        Returns:
            充值历史列表
        """
        params = {"limit": limit}
        if asset:
            params["asset"] = asset
        
        result = self._request("GET", "/api/v1/account/deposits", params=params)
        return result.get('data', result) if isinstance(result, dict) else result
    
    def get_withdraw_history(
        self,
        asset: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        获取提现历史
        
        Args:
            asset: 资产名称（可选）
            limit: 数量限制
        
        Returns:
            提现历史列表
        """
        params = {"limit": limit}
        if asset:
            params["asset"] = asset
        
        result = self._request("GET", "/api/v1/account/withdrawals", params=params)
        return result.get('data', result) if isinstance(result, dict) else result
    
    # ========== 历史数据（5个）==========
    
    def get_order_history(
        self,
        market: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取历史订单
        
        Args:
            market: 市场名称（可选）
            status: 订单状态（可选）
            limit: 数量限制
        
        Returns:
            历史订单列表
        """
        params = {"limit": limit}
        if market:
            params["market"] = market
        if status:
            params["status"] = status
        
        result = self._request("GET", "/api/v1/orders/history", params=params)
        return result.get('data', result) if isinstance(result, dict) else result
    
    def get_trade_history(
        self,
        market: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取成交历史
        
        Args:
            market: 市场名称（可选）
            limit: 数量限制
        
        Returns:
            成交历史列表
        """
        params = {"limit": limit}
        if market:
            params["market"] = market
        
        result = self._request("GET", "/api/v1/trades/history", params=params)
        return result.get('data', result) if isinstance(result, dict) else result
    
    def get_funding_history(
        self,
        market: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取资金费历史
        
        Args:
            market: 市场名称（可选）
            limit: 数量限制
        
        Returns:
            资金费历史列表
        """
        params = {"limit": limit}
        if market:
            params["market"] = market
        
        result = self._request("GET", "/api/v1/funding/history", params=params)
        return result.get('data', result) if isinstance(result, dict) else result
    
    def get_liquidation_history(
        self,
        market: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取强平历史
        
        Args:
            market: 市场名称（可选）
            limit: 数量限制
        
        Returns:
            强平历史列表
        """
        params = {"limit": limit}
        if market:
            params["market"] = market
        
        result = self._request("GET", "/api/v1/liquidations/history", params=params)
        return result.get('data', result) if isinstance(result, dict) else result
    
    def get_pnl_summary(self, period: str = '30d') -> Dict[str, Any]:
        """
        获取盈亏汇总
        
        Args:
            period: 时间周期（7d, 30d, 90d）
        
        Returns:
            盈亏汇总
        """
        params = {"period": period}
        return self._request("GET", "/api/v1/pnl/summary", params=params)
    
    # ========== Smart ADL（4个）==========
    
    def get_smart_adl_config(self) -> Dict[str, Any]:
        """
        获取 Smart ADL 配置
        
        Returns:
            ADL 配置信息
        """
        return self._request("GET", "/api/v1/smart-adl/config")
    
    def update_smart_adl_config(
        self,
        enabled: Optional[bool] = None,
        mode: Optional[str] = None,
        threshold: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        修改 Smart ADL 配置
        
        Args:
            enabled: 是否启用
            mode: 模式
            threshold: 阈值
        
        Returns:
            更新结果
        """
        data = {}
        if enabled is not None:
            data["enabled"] = enabled
        if mode:
            data["mode"] = mode
        if threshold:
            data["threshold"] = threshold
        
        return self._request("PUT", "/api/v1/smart-adl/config", data=data)
    
    def get_protection_pool(self) -> List[Dict[str, Any]]:
        """
        获取保护池信息
        
        Returns:
            保护池列表
        """
        result = self._request("GET", "/api/v1/smart-adl/protection-pool")
        return result.get('data', result) if isinstance(result, dict) else result
    
    def get_smart_adl_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        获取 Smart ADL 历史
        
        Args:
            limit: 数量限制
        
        Returns:
            ADL 历史列表
        """
        params = {"limit": limit}
        result = self._request("GET", "/api/v1/smart-adl/history", params=params)
        return result.get('data', result) if isinstance(result, dict) else result

