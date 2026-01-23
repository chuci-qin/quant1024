"""
1024ex Exchange Modules

模块化架构，每个模块负责一个功能领域：
- PerpModule: 永续合约交易
- SpotModule: 现货交易
- PredictionModule: 预测市场
- ChampionshipModule: 锦标赛排行榜
- AccountModule: 账户管理
"""

from .perp import PerpModule
from .spot import SpotModule
from .prediction import PredictionModule
from .championship import ChampionshipModule
from .account import AccountModule

__all__ = [
    "PerpModule",
    "SpotModule",
    "PredictionModule",
    "ChampionshipModule",
    "AccountModule",
]




