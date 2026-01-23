"""
1024ex Exchange connector

Implements the 1024 Exchange Public API v2.6.0
Supports modular architecture with separate modules for Perp, Spot, Prediction, Championship, and Account.

Authentication: HMAC-SHA256 signature
- Header: X-EXCHANGE-API-KEY (API Key)
- Header: X-SIGNATURE (HMAC-SHA256 signature)
- Header: X-TIMESTAMP (Unix timestamp in milliseconds)
- Header: X-RECV-WINDOW (Optional, default 5000ms)

API Documentation: https://api.1024ex.com/api-docs/openapi.json
"""

import requests
import json
import time
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin

from .base import BaseExchange
from .modules import (
    PerpModule,
    SpotModule,
    PredictionModule,
    ChampionshipModule,
    AccountModule,
)
from ..auth.hmac_auth import get_auth_headers, get_simple_auth_headers
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
    
    采用模块化架构，通过 exchange.perp.xxx() 风格访问各模块 API。
    
    模块:
        - perp: 永续合约交易 (PerpModule)
        - spot: 现货交易 (SpotModule)
        - prediction: 预测市场 (PredictionModule)
        - championship: 锦标赛排行榜 (ChampionshipModule)
        - account: 账户管理 (AccountModule)
    
    认证方式: HMAC-SHA256 签名认证
    
    Example:
        >>> exchange = Exchange1024ex(api_key="xxx", secret_key="xxx")
        >>> 
        >>> # 永续合约
        >>> exchange.perp.get_ticker("BTC-USDC")
        >>> exchange.perp.place_order(market="BTC-USDC", side="long", size="0.1")
        >>> 
        >>> # 现货
        >>> exchange.spot.get_balances()
        >>> 
        >>> # 预测市场
        >>> exchange.prediction.list_markets(category="crypto")
    """
    
    def __init__(
        self,
        api_key: str = "",
        secret_key: str = "",
        base_url: str = "https://api.1024ex.com",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        初始化 1024ex 客户端
        
        Args:
            api_key: Exchange API Key（X-EXCHANGE-API-KEY header）
            secret_key: Exchange Secret Key（用于生成 HMAC-SHA256 签名）
            base_url: API 基础 URL (默认生产环境)
                - 生产环境: https://api.1024ex.com
                - 测试网: https://testnet-api.1024ex.com
                - 本地开发: http://localhost:8090
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
        """
        super().__init__(api_key, secret_key, base_url)
        self.secret_key = secret_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        
        # 初始化模块
        self._perp = PerpModule(self)
        self._spot = SpotModule(self)
        self._prediction = PredictionModule(self)
        self._championship = ChampionshipModule(self)
        self._account = AccountModule(self)
    
    # ========== 模块访问器 ==========
    
    @property
    def perp(self) -> PerpModule:
        """永续合约模块"""
        return self._perp
    
    @property
    def spot(self) -> SpotModule:
        """现货交易模块"""
        return self._spot
    
    @property
    def prediction(self) -> PredictionModule:
        """预测市场模块"""
        return self._prediction
    
    @property
    def championship(self) -> ChampionshipModule:
        """锦标赛模块"""
        return self._championship
    
    @property
    def account(self) -> AccountModule:
        """账户管理模块"""
        return self._account
    
    # ========== HTTP 请求层 ==========
    
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
        
        # 构造认证 Headers
        if auth_required and self.api_key:
            if self.secret_key:
                # 使用 HMAC-SHA256 签名认证（推荐）
                headers = get_auth_headers(
                    api_key=self.api_key,
                    secret_key=self.secret_key,
                    method=method.upper(),
                    path=path,
                    body=body
                )
            else:
                # 仅 API Key 认证（用于公开端点或测试）
                headers = get_simple_auth_headers(self.api_key)
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
                    raise AuthenticationError("认证失败，请检查 API Key")
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
    # 这些是全局接口，保留在主客户端
    
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
    
    # ========== 向后兼容的便捷方法 ==========
    # 委托给 perp 模块，保持旧 API 兼容
    
    def get_markets(self) -> List[Dict[str, Any]]:
        """获取所有市场（委托给 perp 模块）"""
        return self.perp.get_markets()
    
    def get_market(self, market: str) -> Dict[str, Any]:
        """获取单个市场信息（委托给 perp 模块）"""
        return self.perp.get_market(market)
    
    def get_ticker(self, market: str) -> Dict[str, Any]:
        """获取24小时行情（委托给 perp 模块）"""
        return self.perp.get_ticker(market)
    
    def get_orderbook(self, market: str, depth: int = 20) -> Dict[str, Any]:
        """获取订单簿（委托给 perp 模块）"""
        return self.perp.get_orderbook(market, depth)
    
    def get_trades(self, market: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取最近成交（委托给 perp 模块）"""
        return self.perp.get_trades(market, limit)
    
    def get_klines(
        self,
        market: str,
        interval: str = '1h',
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取K线数据（委托给 perp 模块）"""
        return self.perp.get_klines(market, interval, start_time, end_time, limit)
    
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
        """下单（委托给 perp 模块）"""
        return self.perp.place_order(
            market=market,
            side=side,
            order_type=order_type,
            size=size,
            price=price,
            leverage=leverage,
            reduce_only=reduce_only,
            post_only=post_only,
            time_in_force=time_in_force,
            client_order_id=client_order_id
        )
    
    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """撤单（委托给 perp 模块）"""
        return self.perp.cancel_order(order_id)
    
    def cancel_all_orders(self, market: Optional[str] = None) -> Dict[str, Any]:
        """批量撤单（委托给 perp 模块）"""
        return self.perp.cancel_all_orders(market)
    
    def get_orders(
        self,
        market: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """获取当前委托（委托给 perp 模块）"""
        return self.perp.get_orders(market, status)
    
    def get_order(self, order_id: str) -> Dict[str, Any]:
        """获取订单详情（委托给 perp 模块）"""
        return self.perp.get_order(order_id)
    
    def get_positions(self, market: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取持仓（委托给 perp 模块）"""
        return self.perp.get_positions(market)
    
    def get_balance(self) -> Dict[str, Any]:
        """获取账户余额（委托给 account 模块）"""
        return self.account.get_overview()
    
    def get_margin(self) -> Dict[str, Any]:
        """获取保证金信息（委托给 account 模块）"""
        return self.account.get_perp_margin()
    
    def get_funding_rate(self, market: str) -> Dict[str, Any]:
        """获取资金费率（委托给 perp 模块）"""
        return self.perp.get_funding_rate(market)
    
    def get_market_stats(self, market: str) -> Dict[str, Any]:
        """获取市场统计（委托给 perp 模块）"""
        return self.perp.get_open_interest(market)
    
    def update_order(
        self,
        order_id: str,
        price: Optional[str] = None,
        size: Optional[str] = None
    ) -> Dict[str, Any]:
        """修改订单（委托给 perp 模块）"""
        return self.perp.update_order(order_id, price or "", size)
    
    def batch_place_orders(self, orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """批量下单（委托给 perp 模块）"""
        return self.perp.batch_place_orders(orders)
    
    def set_tpsl(
        self,
        market: str,
        tp_price: Optional[str] = None,
        sl_price: Optional[str] = None
    ) -> Dict[str, Any]:
        """设置止盈止损（委托给 perp 模块）"""
        return self.perp.set_tpsl(market, tp_price, sl_price)
    
    def get_leverage(self, market: str) -> Dict[str, Any]:
        """获取杠杆设置（委托给 perp 模块）"""
        return self.perp.get_leverage(market)
    
    def set_leverage(self, market: str, leverage: int) -> Dict[str, Any]:
        """设置杠杆（委托给 perp 模块）"""
        return self.perp.set_leverage(market, leverage)
    
    def get_sub_accounts(self) -> List[Dict[str, Any]]:
        """获取子账户（委托给 account 模块的 API Keys 列表）"""
        return self.account.get_api_keys()
    
    def get_deposit_address(self, asset: str, chain: str = "solana") -> Dict[str, Any]:
        """获取充值地址（委托给 account 模块）"""
        return self.account.initiate_deposit(asset, chain)
    
    def withdraw(
        self,
        asset: str,
        amount: str,
        address: str,
        memo: Optional[str] = None,
        chain: str = "solana"
    ) -> Dict[str, Any]:
        """提现（委托给 account 模块）"""
        return self.account.request_withdrawal(asset, amount, address, chain)
    
    def get_deposit_history(
        self,
        asset: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """获取充值历史（委托给 account 模块）"""
        return self.account.get_deposits()
    
    def get_withdraw_history(
        self,
        asset: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """获取提现历史（委托给 account 模块）"""
        return self.account.get_withdrawals()
    
    def get_order_history(
        self,
        market: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取历史订单（委托给 perp 模块）"""
        return self.perp.get_order_history(market=market, limit=limit)
    
    def get_trade_history(
        self,
        market: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取成交历史（委托给 perp 模块）"""
        return self.perp.get_trade_history(market=market, limit=limit)
    
    def get_funding_history(
        self,
        market: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取资金费历史（委托给 perp 模块）"""
        return self.perp.get_user_funding_history(market=market, limit=limit)
    
    def get_liquidation_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """获取强平历史（委托给 perp 模块）"""
        return self.perp.get_liquidation_history()
    
    def get_pnl_summary(self, period: str = "30d") -> Dict[str, Any]:
        """获取盈亏汇总（委托给 perp 模块）"""
        return self.perp.get_pnl_summary()
    
    def get_smart_adl_config(self) -> Dict[str, Any]:
        """获取 Smart ADL 配置"""
        return self._request("GET", "/api/v1/smart-adl/config")
    
    def update_smart_adl_config(
        self,
        enabled: Optional[bool] = None,
        mode: Optional[str] = None
    ) -> Dict[str, Any]:
        """更新 Smart ADL 配置"""
        data = {}
        if enabled is not None:
            data["enabled"] = enabled
        if mode is not None:
            data["mode"] = mode
        return self._request("PUT", "/api/v1/smart-adl/config", data=data)
    
    def get_protection_pool(self) -> List[Dict[str, Any]]:
        """获取保护池"""
        result = self._request("GET", "/api/v1/smart-adl/protection-pool")
        if isinstance(result, dict) and "data" in result:
            return result["data"]
        return []
    
    def get_smart_adl_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取 Smart ADL 历史"""
        result = self._request("GET", "/api/v1/smart-adl/history", params={"limit": limit})
        if isinstance(result, dict) and "data" in result:
            return result["data"]
        return []