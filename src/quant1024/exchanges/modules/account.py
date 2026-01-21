"""
AccountModule - 账户管理模块

实现 /api/v1/accounts/me/ 下的所有 API 接口，包括：
- 账户概览
- API Key 管理
- 充值/提现
- Perp 保证金
- Spot 资产汇总
- 链上状态
"""

from typing import Any, Dict, List, Optional
from ._base import ModuleBase


class AccountModule(ModuleBase):
    """
    账户管理模块
    
    提供账户管理相关的 API 接口。
    
    Example:
        >>> exchange = Exchange1024ex(api_key="xxx", secret_key="xxx")
        >>> exchange.account.get_overview()
        >>> exchange.account.get_deposits()
    """
    
    PATH_PREFIX = "/api/v1/accounts/me"
    
    # ========== 账户概览 ==========
    
    def get_overview(self) -> Dict[str, Any]:
        """
        获取账户概览
        
        Returns:
            账户信息，包括钱包地址、VIP 等级、总权益、未实现盈亏等
        """
        return self._request("GET", "/overview")
    
    def get_onchain_status(self) -> Dict[str, Any]:
        """
        获取链上账户状态
        
        Returns:
            链上状态，包括可用余额、锁定保证金、未实现盈亏等
        """
        return self._request("GET", "/onchain-status")
    
    # ========== Perp 相关 ==========
    
    def get_perp_margin(self) -> Dict[str, Any]:
        """
        获取 Perp 保证金信息
        
        Returns:
            保证金汇总，包括总保证金、可用保证金、已用保证金、保证金率等
        """
        return self._request("GET", "/perp/margin")
    
    def get_perp_trading_stats(self) -> Dict[str, Any]:
        """
        获取 Perp 交易统计
        
        Returns:
            交易统计，包括总交易次数、总交易量、盈亏、胜率等
        """
        return self._request("GET", "/perp/trading-stats")
    
    # ========== Spot 相关 ==========
    
    def get_spot_summary(self) -> Dict[str, Any]:
        """
        获取 Spot 资产汇总
        
        Returns:
            资产汇总，包括总价值、代币数量、Top 持仓等
        """
        return self._request("GET", "/spot/summary")
    
    # ========== API Key 管理 ==========
    
    def get_api_keys(self) -> List[Dict[str, Any]]:
        """获取 API Key 列表"""
        result = self._request("GET", "/api-keys")
        return self._extract_data(result)
    
    def get_api_key(self, key_id: str) -> Dict[str, Any]:
        """获取单个 API Key 信息"""
        return self._request("GET", f"/api-keys/{key_id}")
    
    # ========== 充值 ==========
    
    def get_deposits(self) -> List[Dict[str, Any]]:
        """获取充值历史"""
        result = self._request("GET", "/deposits")
        return self._extract_data(result)
    
    def initiate_deposit(self, token: str, chain: str) -> Dict[str, Any]:
        """
        获取充值地址
        
        Args:
            token: 代币符号 (如 USDC)
            chain: 链名称 (如 solana)
        
        Returns:
            充值地址信息
        """
        data = {"token": token, "chain": chain}
        return self._request("POST", "/deposits", data=data)
    
    # ========== 提现 ==========
    
    def get_withdrawals(self) -> List[Dict[str, Any]]:
        """获取提现历史"""
        result = self._request("GET", "/withdrawals")
        return self._extract_data(result)
    
    def request_withdrawal(
        self,
        token: str,
        amount: str,
        destination: str,
        chain: str
    ) -> Dict[str, Any]:
        """
        请求提现
        
        Args:
            token: 代币符号
            amount: 提现数量
            destination: 目标地址
            chain: 链名称
        
        Returns:
            提现信息，包括提现 ID、手续费、预计到账时间等
        """
        data = {
            "token": token,
            "amount": amount,
            "destination": destination,
            "chain": chain
        }
        return self._request("POST", "/withdrawals", data=data)
