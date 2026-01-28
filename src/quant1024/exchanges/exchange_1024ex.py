"""
1024ex Exchange Connector

Implements the 1024 Exchange Public API v4.1.0
Supports modular architecture with separate modules for Perp, Spot, Prediction, Championship, and Account.

Authentication: HMAC-SHA256 signature
- Header: X-TRADING-API-KEY (Trading API Key)
- Header: X-SIGNATURE (HMAC-SHA256 signature)
- Header: X-TIMESTAMP (Unix timestamp in milliseconds)

Signature formula:
    message = timestamp + METHOD + path + body
    signature = hex(HMAC-SHA256(secret_key, message))

Note: Timestamp must be within 30 seconds of server time.

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
    1024 Exchange Connector
    
    Modular architecture with access to various APIs via exchange.perp.xxx() style.
    
    Modules:
        - perp: Perpetual futures trading (PerpModule)
        - spot: Spot trading (SpotModule)
        - prediction: Prediction markets (PredictionModule)
        - championship: Championship leaderboard (ChampionshipModule)
        - account: Account management (AccountModule)
    
    Authentication: HMAC-SHA256 signature
    
    Example:
        >>> exchange = Exchange1024ex(api_key="1024_xxx", secret_key="xxx")
        >>> 
        >>> # Perpetual futures
        >>> exchange.perp.get_ticker("BTC-USDC")
        >>> exchange.perp.place_order(market="BTC-USDC", side="long", size="0.1")
        >>> 
        >>> # Spot trading
        >>> exchange.spot.get_balances()
        >>> 
        >>> # Prediction markets
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
        Initialize 1024ex client.
        
        Args:
            api_key: Trading API Key (for X-TRADING-API-KEY header)
            secret_key: Trading API Secret Key (for HMAC-SHA256 signature)
            base_url: API base URL (default: production)
                - Production: https://api.1024ex.com
                - Testnet: https://testnet-api.1024ex.com
                - Local dev: http://localhost:8090
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for failed requests
        """
        super().__init__(api_key, secret_key, base_url)
        self.secret_key = secret_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()
        
        # Initialize modules
        self._perp = PerpModule(self)
        self._spot = SpotModule(self)
        self._prediction = PredictionModule(self)
        self._championship = ChampionshipModule(self)
        self._account = AccountModule(self)
    
    # ========== Module Accessors ==========
    
    @property
    def perp(self) -> PerpModule:
        """Perpetual futures trading module"""
        return self._perp
    
    @property
    def spot(self) -> SpotModule:
        """Spot trading module"""
        return self._spot
    
    @property
    def prediction(self) -> PredictionModule:
        """Prediction markets module"""
        return self._prediction
    
    @property
    def championship(self) -> ChampionshipModule:
        """Championship leaderboard module"""
        return self._championship
    
    @property
    def account(self) -> AccountModule:
        """Account management module"""
        return self._account
    
    # ========== HTTP Request Layer ==========
    
    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        auth_required: bool = True
    ) -> Dict[str, Any]:
        """
        Send HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API endpoint path
            params: URL query parameters
            data: Request body data
            auth_required: Whether authentication is required
        
        Returns:
            API response data
        
        Raises:
            APIError: General API error
            AuthenticationError: Authentication failed
            RateLimitError: Rate limit exceeded
        """
        url = urljoin(self.base_url, path)
        
        # Build request body
        body = ""
        if data:
            body = json.dumps(data)
        
        # Build authentication headers
        if auth_required and self.api_key:
            if self.secret_key:
                # Use HMAC-SHA256 signature authentication (recommended)
                headers = get_auth_headers(
                    api_key=self.api_key,
                    secret_key=self.secret_key,
                    method=method.upper(),
                    path=path,
                    body=body
                )
            else:
                # API Key only (for public endpoints or testing)
                headers = get_simple_auth_headers(self.api_key)
        else:
            headers = {"Content-Type": "application/json"}
        
        # Send request with retry logic
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
                
                # Handle HTTP errors
                if response.status_code == 401:
                    raise AuthenticationError("Authentication failed. Please check your API Key and Secret.")
                elif response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    raise RateLimitError(f"Rate limited. Please wait {retry_after} seconds.")
                elif response.status_code == 404:
                    raise MarketNotFoundError("Resource not found")
                elif response.status_code >= 400:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('message', f'HTTP {response.status_code}')
                    except:
                        error_msg = f'HTTP {response.status_code}'
                    raise APIError(error_msg)
                
                # Parse response
                try:
                    result = response.json()
                    return result
                except ValueError:
                    return {"success": True, "data": response.text}
            
            except (requests.ConnectionError, requests.Timeout) as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    raise APIError(f"Request failed: {str(e)}")
            
            except RateLimitError:
                raise  # Don't retry rate limit errors
            
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
        
        if last_exception:
            raise APIError(f"Request failed: {str(last_exception)}")
        
        return {}
    
    # ========== System Endpoints (3) ==========
    # Global endpoints, kept on main client
    
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
    
    # ========== Backward-Compatible Convenience Methods ==========
    # Delegates to perp/account modules for legacy API compatibility
    
    def get_markets(self) -> List[Dict[str, Any]]:
        """Get all markets (delegates to perp module)"""
        return self.perp.get_markets()
    
    def get_market(self, market: str) -> Dict[str, Any]:
        """Get single market info (delegates to perp module)"""
        return self.perp.get_market(market)
    
    def get_ticker(self, market: str) -> Dict[str, Any]:
        """Get 24h ticker (delegates to perp module)"""
        return self.perp.get_ticker(market)
    
    def get_orderbook(self, market: str, depth: int = 20) -> Dict[str, Any]:
        """Get orderbook (delegates to perp module)"""
        return self.perp.get_orderbook(market, depth)
    
    def get_trades(self, market: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent trades (delegates to perp module)"""
        return self.perp.get_trades(market, limit)
    
    def get_klines(
        self,
        market: str,
        interval: str = '1h',
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get candlestick data (delegates to perp module)"""
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
        """Place order (delegates to perp module)"""
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
        """Cancel order (delegates to perp module)"""
        return self.perp.cancel_order(order_id)
    
    def cancel_all_orders(self, market: Optional[str] = None) -> Dict[str, Any]:
        """Cancel all orders (delegates to perp module)"""
        return self.perp.cancel_all_orders(market)
    
    def get_orders(
        self,
        market: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get open orders (delegates to perp module)"""
        return self.perp.get_orders(market, status)
    
    def get_order(self, order_id: str) -> Dict[str, Any]:
        """Get order details (delegates to perp module)"""
        return self.perp.get_order(order_id)
    
    def get_positions(self, market: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get positions (delegates to perp module)"""
        return self.perp.get_positions(market)
    
    def get_balance(self) -> Dict[str, Any]:
        """Get account balance (delegates to account module)"""
        return self.account.get_overview()
    
    def get_margin(self) -> Dict[str, Any]:
        """Get margin info (delegates to account module)"""
        return self.account.get_perp_margin()
    
    def get_funding_rate(self, market: str) -> Dict[str, Any]:
        """Get funding rate (delegates to perp module)"""
        return self.perp.get_funding_rate(market)
    
    def get_market_stats(self, market: str) -> Dict[str, Any]:
        """Get market stats (delegates to perp module)"""
        return self.perp.get_open_interest(market)
    
    def update_order(
        self,
        order_id: str,
        price: Optional[str] = None,
        size: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update order (delegates to perp module)"""
        return self.perp.update_order(order_id, price or "", size)
    
    def batch_place_orders(self, orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Batch place orders (delegates to perp module)"""
        return self.perp.batch_place_orders(orders)
    
    def set_tpsl(
        self,
        market: str,
        tp_price: Optional[str] = None,
        sl_price: Optional[str] = None
    ) -> Dict[str, Any]:
        """Set take-profit/stop-loss (delegates to perp module)"""
        return self.perp.set_tpsl(market, tp_price, sl_price)
    
    def get_leverage(self, market: str) -> Dict[str, Any]:
        """Get leverage setting (delegates to perp module)"""
        return self.perp.get_leverage(market)
    
    def set_leverage(self, market: str, leverage: int) -> Dict[str, Any]:
        """Set leverage (delegates to perp module)"""
        return self.perp.set_leverage(market, leverage)
    
    def get_sub_accounts(self) -> List[Dict[str, Any]]:
        """Get sub-accounts (delegates to account module's API keys list)"""
        return self.account.get_api_keys()
    
    def get_deposit_address(self, asset: str, chain: str = "solana") -> Dict[str, Any]:
        """Get deposit address (delegates to account module)"""
        return self.account.initiate_deposit(asset, chain)
    
    def withdraw(
        self,
        asset: str,
        amount: str,
        address: str,
        memo: Optional[str] = None,
        chain: str = "solana"
    ) -> Dict[str, Any]:
        """Withdraw funds (delegates to account module)"""
        return self.account.request_withdrawal(asset, amount, address, chain)
    
    def get_deposit_history(
        self,
        asset: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get deposit history (delegates to account module)"""
        return self.account.get_deposits()
    
    def get_withdraw_history(
        self,
        asset: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get withdrawal history (delegates to account module)"""
        return self.account.get_withdrawals()
    
    def get_order_history(
        self,
        market: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get order history (delegates to perp module)"""
        return self.perp.get_order_history(market=market, limit=limit)
    
    def get_trade_history(
        self,
        market: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get trade history (delegates to perp module)"""
        return self.perp.get_trade_history(market=market, limit=limit)
    
    def get_funding_history(
        self,
        market: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get funding payment history (delegates to perp module)"""
        return self.perp.get_user_funding_history(market=market, limit=limit)
    
    def get_liquidation_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get liquidation history (delegates to perp module)"""
        return self.perp.get_liquidation_history()
    
    def get_pnl_summary(self, period: str = "30d") -> Dict[str, Any]:
        """Get PnL summary (delegates to perp module)"""
        return self.perp.get_pnl_summary()
    
    def get_smart_adl_config(self) -> Dict[str, Any]:
        """Get Smart ADL configuration"""
        return self._request("GET", "/api/v1/smart-adl/config")
    
    def update_smart_adl_config(
        self,
        enabled: Optional[bool] = None,
        mode: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update Smart ADL configuration"""
        data = {}
        if enabled is not None:
            data["enabled"] = enabled
        if mode is not None:
            data["mode"] = mode
        return self._request("PUT", "/api/v1/smart-adl/config", data=data)
    
    def get_protection_pool(self) -> List[Dict[str, Any]]:
        """Get protection pool"""
        result = self._request("GET", "/api/v1/smart-adl/protection-pool")
        if isinstance(result, dict) and "data" in result:
            return result["data"]
        return []
    
    def get_smart_adl_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get Smart ADL history"""
        result = self._request("GET", "/api/v1/smart-adl/history", params={"limit": limit})
        if isinstance(result, dict) and "data" in result:
            return result["data"]
        return []