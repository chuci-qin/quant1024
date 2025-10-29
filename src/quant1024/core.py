"""
Core functionality for quant1024 package
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any


class QuantStrategy(ABC):
    """
    抽象基类：量化交易策略
    
    这是一个抽象类，用于定义量化交易策略的基本接口。
    其他软件可以继承这个类来实现自己的交易策略。
    """
    
    def __init__(self, name: str, params: Optional[Dict[str, Any]] = None):
        """
        初始化策略
        
        Args:
            name: 策略名称
            params: 策略参数字典
        """
        self.name = name
        self.params = params or {}
        self._is_initialized = False
    
    def initialize(self) -> None:
        """初始化策略"""
        self._is_initialized = True
        print(f"Strategy '{self.name}' initialized with params: {self.params}")
    
    @abstractmethod
    def generate_signals(self, data: List[float]) -> List[int]:
        """
        生成交易信号（抽象方法，必须由子类实现）
        
        Args:
            data: 价格数据列表
            
        Returns:
            信号列表，1表示买入，-1表示卖出，0表示持有
        """
        pass
    
    @abstractmethod
    def calculate_position(self, signal: int, current_position: float) -> float:
        """
        根据信号计算仓位（抽象方法，必须由子类实现）
        
        Args:
            signal: 交易信号 (1买入, -1卖出, 0持有)
            current_position: 当前仓位
            
        Returns:
            新的仓位大小
        """
        pass
    
    def backtest(self, data: List[float]) -> Dict[str, Any]:
        """
        回测策略
        
        Args:
            data: 历史价格数据
            
        Returns:
            回测结果字典
        """
        if not self._is_initialized:
            self.initialize()
        
        signals = self.generate_signals(data)
        returns = calculate_returns(data)
        sharpe = calculate_sharpe_ratio(returns)
        
        return {
            "strategy_name": self.name,
            "total_signals": len(signals),
            "buy_signals": signals.count(1),
            "sell_signals": signals.count(-1),
            "sharpe_ratio": sharpe
        }


def calculate_returns(prices: List[float]) -> List[float]:
    """
    计算收益率
    
    Args:
        prices: 价格序列
        
    Returns:
        收益率序列
    """
    if len(prices) < 2:
        return []
    
    returns = []
    for i in range(1, len(prices)):
        if prices[i-1] != 0:
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
        else:
            returns.append(0.0)
    
    return returns


def calculate_sharpe_ratio(returns: List[float], risk_free_rate: float = 0.0) -> float:
    """
    计算夏普比率
    
    Args:
        returns: 收益率序列
        risk_free_rate: 无风险利率
        
    Returns:
        夏普比率
    """
    if not returns:
        return 0.0
    
    avg_return = sum(returns) / len(returns)
    
    if len(returns) < 2:
        return 0.0
    
    variance = sum((r - avg_return) ** 2 for r in returns) / (len(returns) - 1)
    std_dev = variance ** 0.5
    
    if std_dev == 0:
        return 0.0
    
    sharpe = (avg_return - risk_free_rate) / std_dev
    return sharpe

