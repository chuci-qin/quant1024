"""
Data Model Definitions
"""

from dataclasses import dataclass


@dataclass
class QCCredentials:
    """QuantConnect API credentials"""
    user_id: str
    api_token: str


@dataclass
class BacktestConfig:
    """Backtest configuration"""
    start_date: tuple  # (year, month, day)
    end_date: tuple    # (year, month, day)
    initial_cash: int = 1_000_000
    benchmark: str = "SPY"
