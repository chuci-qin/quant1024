"""
Account models
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class AssetBalance(BaseModel):
    """资产余额"""
    asset: str = Field(..., description="资产名称，如 USDC")
    total: str = Field(..., description="总余额")
    available: str = Field(..., description="可用余额")
    locked: str = Field(..., description="冻结余额")


class Balance(BaseModel):
    """账户余额"""
    balances: List[AssetBalance]
    total_equity: Optional[str] = Field(None, description="总权益")
    total_margin: Optional[str] = Field(None, description="总保证金")
    available_margin: Optional[str] = Field(None, description="可用保证金")


class Margin(BaseModel):
    """保证金信息"""
    total_margin: str = Field(..., description="总保证金")
    used_margin: str = Field(..., description="已用保证金")
    available_margin: str = Field(..., description="可用保证金")
    margin_ratio: str = Field(..., description="保证金率")
    maintenance_margin: str = Field(..., description="维持保证金")


class SubAccount(BaseModel):
    """子账户信息"""
    sub_account_id: str
    nickname: str
    status: str
    created_at: int

