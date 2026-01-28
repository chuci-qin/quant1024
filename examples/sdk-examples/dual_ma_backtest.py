#!/usr/bin/env python3
"""
双均线策略回测 (Dual Moving Average Crossover Strategy)

策略原理:
- 当短期均线上穿长期均线时（金叉），买入
- 当短期均线下穿长期均线时（死叉），卖出

使用方法:
    # 使用默认参数回测 (5日/20日均线, BTC-USD, 使用SDK的DataRetriever)
    python dual_ma_backtest.py

    # 自定义参数
    python dual_ma_backtest.py --symbol ETH-USD --short-ma 10 --long-ma 50 --days 365

    # 使用 1024ex 数据源 (需要API配置)
    python dual_ma_backtest.py --source 1024ex --symbol BTC-PERP --days 180

    # 保存回测报告
    python dual_ma_backtest.py --report backtest_report.md

功能特点:
    ✅ 使用 quant1024 SDK 获取数据
    ✅ 支持多数据源 (1024ex, Yahoo Finance, Binance)
    ✅ 可配置均线周期
    ✅ 完整回测统计 (夏普比率, 最大回撤, 胜率等)
    ✅ 交易记录输出
    ✅ 可视化图表 (可选)
"""

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from quant1024 import DataRetriever, QuantStrategy, calculate_sharpe_ratio


# =============================================================================
# API 配置加载
# =============================================================================

def load_api_config(config_path: str = None) -> dict:
    """
    加载 API 配置文件
    
    Args:
        config_path: 配置文件路径，默认查找项目根目录的 1024-trading-api-key-quant.json
    
    Returns:
        配置字典 {api_key, secret_key, ...}
    """
    if config_path is None:
        # 默认查找项目根目录 (1024ex/)
        config_path = Path(__file__).parent.parent.parent.parent / "1024-trading-api-key-quant.json"
    
    config_path = Path(config_path)
    
    if not config_path.exists():
        return None  # 配置文件不存在，返回 None
    
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        
        # 验证必要字段
        if "api_key" in config and "secret_key" in config:
            return config
        return None
    except Exception:
        return None


# =============================================================================
# 策略配置
# =============================================================================

@dataclass
class StrategyConfig:
    """策略配置参数"""
    short_ma_period: int = 5          # 短期均线周期
    long_ma_period: int = 20          # 长期均线周期
    initial_capital: float = 10000.0  # 初始资金
    position_size: float = 1.0        # 仓位比例 (1.0 = 全仓)
    slippage: float = 0.001           # 滑点 (0.1%)
    commission: float = 0.001         # 手续费 (0.1%)


# =============================================================================
# 交易记录
# =============================================================================

@dataclass
class Trade:
    """单笔交易记录"""
    entry_date: datetime
    entry_price: float
    exit_date: Optional[datetime] = None
    exit_price: Optional[float] = None
    direction: str = "long"           # "long" 或 "short"
    size: float = 0.0
    pnl: float = 0.0
    pnl_pct: float = 0.0
    
    @property
    def is_closed(self) -> bool:
        return self.exit_date is not None


# =============================================================================
# 双均线策略
# =============================================================================

class DualMAStrategy(QuantStrategy):
    """
    双均线交叉策略
    
    信号逻辑:
    - 金叉 (短期均线上穿长期均线): 买入信号 (+1)
    - 死叉 (短期均线下穿长期均线): 卖出信号 (-1)
    - 其他情况: 持有 (0)
    """
    
    def __init__(self, config: StrategyConfig):
        super().__init__(
            name="DualMA",
            params={
                "short_ma": config.short_ma_period,
                "long_ma": config.long_ma_period
            }
        )
        self.config = config
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """
        生成交易信号
        
        Args:
            data: 包含 'close' 列的 DataFrame
            
        Returns:
            信号序列: 1=买入, -1=卖出, 0=持有
        """
        close = data['close']
        
        # 计算均线
        short_ma = close.rolling(window=self.config.short_ma_period).mean()
        long_ma = close.rolling(window=self.config.long_ma_period).mean()
        
        # 生成原始信号
        signals = pd.Series(0, index=data.index)
        
        # 金叉: 短期均线 > 长期均线 (且前一根K线是 短期 <= 长期)
        golden_cross = (short_ma > long_ma) & (short_ma.shift(1) <= long_ma.shift(1))
        signals[golden_cross] = 1
        
        # 死叉: 短期均线 < 长期均线 (且前一根K线是 短期 >= 长期)
        death_cross = (short_ma < long_ma) & (short_ma.shift(1) >= long_ma.shift(1))
        signals[death_cross] = -1
        
        return signals
    
    def calculate_position(self, signal: int, current_position: float) -> float:
        """
        根据信号计算目标仓位
        
        Args:
            signal: 交易信号 (1=买入, -1=卖出, 0=持有)
            current_position: 当前仓位
            
        Returns:
            目标仓位 (0~1)
        """
        if signal == 1:
            return self.config.position_size  # 买入信号 -> 满仓
        elif signal == -1:
            return 0.0  # 卖出信号 -> 清仓
        else:
            return current_position  # 持有 -> 保持现有仓位


# =============================================================================
# 回测引擎
# =============================================================================

class BacktestEngine:
    """
    回测引擎
    
    支持:
    - 滑点和手续费模拟
    - 交易记录
    - 绩效统计
    """
    
    def __init__(self, strategy: DualMAStrategy, data: pd.DataFrame):
        self.strategy = strategy
        self.data = data.copy()
        self.config = strategy.config
        
        # 回测结果
        self.trades: List[Trade] = []
        self.equity_curve: pd.Series = None
        self.signals: pd.Series = None
        
    def run(self) -> Dict[str, Any]:
        """
        运行回测
        
        Returns:
            回测结果字典
        """
        # 生成信号
        self.signals = self.strategy.generate_signals(self.data)
        
        # 初始化状态
        capital = self.config.initial_capital
        position = 0.0  # 持仓数量
        position_value = 0.0
        entry_price = 0.0
        
        equity = []
        current_trade: Optional[Trade] = None
        
        # 遍历每根K线
        for i in range(len(self.data)):
            row = self.data.iloc[i]
            signal = self.signals.iloc[i]
            price = row['close']
            timestamp = row['timestamp'] if 'timestamp' in row.index else row.name
            
            # 计算当前权益
            current_equity = capital + (position * price)
            
            # 处理信号
            if signal == 1 and position == 0:
                # 买入信号 & 当前无仓位 -> 开多
                trade_price = price * (1 + self.config.slippage)  # 滑点
                trade_value = capital * self.config.position_size
                commission = trade_value * self.config.commission
                
                position = (trade_value - commission) / trade_price
                capital = capital - trade_value
                entry_price = trade_price
                
                current_trade = Trade(
                    entry_date=timestamp,
                    entry_price=trade_price,
                    direction="long",
                    size=position
                )
                
            elif signal == -1 and position > 0:
                # 卖出信号 & 当前有仓位 -> 平仓
                trade_price = price * (1 - self.config.slippage)  # 滑点
                trade_value = position * trade_price
                commission = trade_value * self.config.commission
                
                capital = capital + trade_value - commission
                
                if current_trade:
                    current_trade.exit_date = timestamp
                    current_trade.exit_price = trade_price
                    current_trade.pnl = (trade_price - current_trade.entry_price) * current_trade.size - commission * 2
                    current_trade.pnl_pct = (trade_price / current_trade.entry_price - 1) * 100
                    self.trades.append(current_trade)
                    current_trade = None
                
                position = 0.0
                entry_price = 0.0
            
            # 记录权益
            current_equity = capital + (position * price)
            equity.append(current_equity)
        
        # 如果最后还有持仓，计算未平仓盈亏
        if position > 0 and current_trade:
            final_price = self.data.iloc[-1]['close']
            current_trade.exit_date = self.data.iloc[-1]['timestamp'] if 'timestamp' in self.data.columns else None
            current_trade.exit_price = final_price
            current_trade.pnl = (final_price - current_trade.entry_price) * current_trade.size
            current_trade.pnl_pct = (final_price / current_trade.entry_price - 1) * 100
            self.trades.append(current_trade)
        
        # 保存权益曲线
        self.equity_curve = pd.Series(equity, index=self.data.index)
        
        # 计算统计指标
        return self._calculate_statistics()
    
    def _calculate_statistics(self) -> Dict[str, Any]:
        """计算回测统计指标"""
        equity = self.equity_curve
        returns = equity.pct_change().dropna()
        
        # 基础统计
        initial_capital = self.config.initial_capital
        final_capital = equity.iloc[-1]
        total_return = (final_capital / initial_capital - 1) * 100
        
        # 交易统计
        total_trades = len(self.trades)
        winning_trades = len([t for t in self.trades if t.pnl > 0])
        losing_trades = len([t for t in self.trades if t.pnl < 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # 盈亏统计
        if self.trades:
            avg_win = np.mean([t.pnl for t in self.trades if t.pnl > 0]) if winning_trades > 0 else 0
            avg_loss = abs(np.mean([t.pnl for t in self.trades if t.pnl < 0])) if losing_trades > 0 else 0
            profit_factor = (avg_win * winning_trades) / (avg_loss * losing_trades) if losing_trades > 0 and avg_loss > 0 else float('inf')
            max_win = max([t.pnl for t in self.trades]) if self.trades else 0
            max_loss = min([t.pnl for t in self.trades]) if self.trades else 0
        else:
            avg_win = avg_loss = profit_factor = max_win = max_loss = 0
        
        # 风险指标
        sharpe_ratio = calculate_sharpe_ratio(returns.tolist()) * np.sqrt(252)  # 年化
        
        # 最大回撤
        cummax = equity.cummax()
        drawdown = (equity - cummax) / cummax
        max_drawdown = abs(drawdown.min()) * 100
        
        # 年化收益
        days = len(self.data)
        annualized_return = ((final_capital / initial_capital) ** (365 / days) - 1) * 100 if days > 0 else 0
        
        # 波动率
        volatility = returns.std() * np.sqrt(252) * 100
        
        return {
            "strategy_name": self.strategy.name,
            "parameters": self.strategy.params,
            
            # 收益指标
            "initial_capital": initial_capital,
            "final_capital": round(final_capital, 2),
            "total_return_pct": round(total_return, 2),
            "annualized_return_pct": round(annualized_return, 2),
            
            # 风险指标
            "sharpe_ratio": round(sharpe_ratio, 3),
            "max_drawdown_pct": round(max_drawdown, 2),
            "volatility_pct": round(volatility, 2),
            
            # 交易统计
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate_pct": round(win_rate, 2),
            "profit_factor": round(profit_factor, 2) if profit_factor != float('inf') else "∞",
            
            # 盈亏统计
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "max_win": round(max_win, 2),
            "max_loss": round(max_loss, 2),
            
            # 其他
            "data_points": len(self.data),
            "data_start": str(self.data['timestamp'].iloc[0]) if 'timestamp' in self.data.columns else "N/A",
            "data_end": str(self.data['timestamp'].iloc[-1]) if 'timestamp' in self.data.columns else "N/A",
        }
    
    def get_trades_df(self) -> pd.DataFrame:
        """返回交易记录 DataFrame"""
        if not self.trades:
            return pd.DataFrame()
        
        records = []
        for i, t in enumerate(self.trades, 1):
            records.append({
                "序号": i,
                "开仓时间": t.entry_date,
                "开仓价格": round(t.entry_price, 2),
                "平仓时间": t.exit_date,
                "平仓价格": round(t.exit_price, 2) if t.exit_price else None,
                "方向": t.direction,
                "数量": round(t.size, 6),
                "盈亏": round(t.pnl, 2),
                "收益率%": round(t.pnl_pct, 2)
            })
        
        return pd.DataFrame(records)
    
    def plot_results(self, save_path: Optional[str] = None):
        """
        绘制回测结果图表
        
        Args:
            save_path: 保存路径 (可选)
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib.dates as mdates
        except ImportError:
            print("⚠️  需要安装 matplotlib: pip install matplotlib")
            return
        
        fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
        fig.suptitle(f'双均线策略回测结果 ({self.strategy.params["short_ma"]}/{self.strategy.params["long_ma"]})', 
                     fontsize=14, fontweight='bold')
        
        # 准备时间轴
        if 'timestamp' in self.data.columns:
            x = pd.to_datetime(self.data['timestamp'])
        else:
            x = self.data.index
        
        # 图1: 价格和均线
        ax1 = axes[0]
        close = self.data['close']
        short_ma = close.rolling(window=self.strategy.config.short_ma_period).mean()
        long_ma = close.rolling(window=self.strategy.config.long_ma_period).mean()
        
        ax1.plot(x, close, label='价格', color='#333333', linewidth=1)
        ax1.plot(x, short_ma, label=f'MA{self.strategy.config.short_ma_period}', color='#2196F3', linewidth=1.2)
        ax1.plot(x, long_ma, label=f'MA{self.strategy.config.long_ma_period}', color='#FF5722', linewidth=1.2)
        
        # 标记买卖点
        buy_signals = self.signals == 1
        sell_signals = self.signals == -1
        ax1.scatter(x[buy_signals], close[buy_signals], marker='^', color='green', s=100, label='买入', zorder=5)
        ax1.scatter(x[sell_signals], close[sell_signals], marker='v', color='red', s=100, label='卖出', zorder=5)
        
        ax1.set_ylabel('价格')
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # 图2: 权益曲线
        ax2 = axes[1]
        ax2.fill_between(x, self.equity_curve, alpha=0.3, color='#4CAF50')
        ax2.plot(x, self.equity_curve, color='#4CAF50', linewidth=1.5, label='权益曲线')
        ax2.axhline(y=self.config.initial_capital, color='gray', linestyle='--', alpha=0.5, label='初始资金')
        ax2.set_ylabel('权益')
        ax2.legend(loc='upper left')
        ax2.grid(True, alpha=0.3)
        
        # 图3: 回撤
        ax3 = axes[2]
        cummax = self.equity_curve.cummax()
        drawdown = (self.equity_curve - cummax) / cummax * 100
        ax3.fill_between(x, drawdown, 0, alpha=0.3, color='#F44336')
        ax3.plot(x, drawdown, color='#F44336', linewidth=1)
        ax3.set_ylabel('回撤 (%)')
        ax3.set_xlabel('日期')
        ax3.grid(True, alpha=0.3)
        
        # 格式化x轴
        for ax in axes:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"✅ 图表已保存到: {save_path}")
        else:
            plt.show()


# =============================================================================
# 结果打印
# =============================================================================

def generate_markdown_report(
    results: Dict[str, Any], 
    trades_df: pd.DataFrame,
    engine: 'BacktestEngine',
    args: argparse.Namespace
) -> str:
    """
    生成 Markdown 格式的回测报告
    
    Args:
        results: 回测统计结果
        trades_df: 交易记录 DataFrame
        engine: 回测引擎实例
        args: 命令行参数
        
    Returns:
        Markdown 格式的报告字符串
    """
    report = []
    
    # 标题
    report.append("# 📊 双均线策略回测报告")
    report.append("")
    report.append(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # 策略配置
    report.append("## 📋 策略配置")
    report.append("")
    report.append("| 参数 | 值 |")
    report.append("|------|-----|")
    report.append(f"| 策略名称 | {results['strategy_name']} |")
    report.append(f"| 短期均线 | MA{results['parameters']['short_ma']} |")
    report.append(f"| 长期均线 | MA{results['parameters']['long_ma']} |")
    report.append(f"| 数据源 | {args.source} |")
    report.append(f"| 交易标的 | {args.symbol} |")
    report.append(f"| K线周期 | {args.interval} |")
    report.append(f"| 初始资金 | ${results['initial_capital']:,.2f} |")
    report.append(f"| 仓位比例 | {args.position_size * 100:.0f}% |")
    report.append(f"| 滑点 | {args.slippage * 100:.2f}% |")
    report.append(f"| 手续费 | {args.commission * 100:.2f}% |")
    report.append("")
    
    # 数据范围
    report.append("## 📅 数据范围")
    report.append("")
    report.append(f"- **开始日期**: {results['data_start']}")
    report.append(f"- **结束日期**: {results['data_end']}")
    report.append(f"- **数据点数**: {results['data_points']}")
    report.append("")
    
    # 收益指标
    report.append("## 💰 收益指标")
    report.append("")
    report.append("| 指标 | 值 |")
    report.append("|------|-----|")
    report.append(f"| 初始资金 | ${results['initial_capital']:,.2f} |")
    report.append(f"| 最终资金 | ${results['final_capital']:,.2f} |")
    
    total_return = results['total_return_pct']
    return_emoji = "📈" if total_return > 0 else "📉"
    report.append(f"| 总收益率 | {return_emoji} **{total_return:+.2f}%** |")
    report.append(f"| 年化收益 | {results['annualized_return_pct']:+.2f}% |")
    report.append("")
    
    # 风险指标
    report.append("## 📉 风险指标")
    report.append("")
    report.append("| 指标 | 值 | 说明 |")
    report.append("|------|-----|------|")
    
    sharpe = results['sharpe_ratio']
    sharpe_rating = "优秀" if sharpe > 1 else ("良好" if sharpe > 0.5 else ("一般" if sharpe > 0 else "差"))
    report.append(f"| 夏普比率 | {sharpe:.3f} | {sharpe_rating} |")
    
    max_dd = results['max_drawdown_pct']
    dd_rating = "低风险" if max_dd < 10 else ("中风险" if max_dd < 20 else "高风险")
    report.append(f"| 最大回撤 | {max_dd:.2f}% | {dd_rating} |")
    report.append(f"| 波动率 | {results['volatility_pct']:.2f}% | 年化 |")
    report.append("")
    
    # 交易统计
    report.append("## 🎯 交易统计")
    report.append("")
    report.append("| 指标 | 值 |")
    report.append("|------|-----|")
    report.append(f"| 总交易次数 | {results['total_trades']} |")
    report.append(f"| 盈利次数 | {results['winning_trades']} ✅ |")
    report.append(f"| 亏损次数 | {results['losing_trades']} ❌ |")
    report.append(f"| 胜率 | {results['win_rate_pct']:.2f}% |")
    report.append(f"| 盈亏比 | {results['profit_factor']} |")
    report.append("")
    
    # 盈亏统计
    report.append("## 💵 盈亏统计")
    report.append("")
    report.append("| 指标 | 值 |")
    report.append("|------|-----|")
    report.append(f"| 平均盈利 | ${results['avg_win']:,.2f} |")
    report.append(f"| 平均亏损 | ${results['avg_loss']:,.2f} |")
    report.append(f"| 最大盈利 | ${results['max_win']:,.2f} |")
    report.append(f"| 最大亏损 | ${results['max_loss']:,.2f} |")
    report.append("")
    
    # 交易记录
    if not trades_df.empty:
        report.append("## 📝 交易记录")
        report.append("")
        report.append("| # | 开仓时间 | 开仓价格 | 平仓时间 | 平仓价格 | 方向 | 盈亏 | 收益率 |")
        report.append("|---|----------|----------|----------|----------|------|------|--------|")
        
        for _, row in trades_df.iterrows():
            entry_time = str(row['开仓时间'])[:10] if row['开仓时间'] else '-'
            exit_time = str(row['平仓时间'])[:10] if row['平仓时间'] else '-'
            pnl = row['盈亏']
            pnl_str = f"${pnl:,.2f}" if pnl >= 0 else f"-${abs(pnl):,.2f}"
            pnl_emoji = "🟢" if pnl > 0 else ("🔴" if pnl < 0 else "⚪")
            
            report.append(
                f"| {row['序号']} | {entry_time} | ${row['开仓价格']:,.2f} | "
                f"{exit_time} | ${row['平仓价格']:,.2f} | {row['方向']} | "
                f"{pnl_emoji} {pnl_str} | {row['收益率%']:+.2f}% |"
            )
        report.append("")
    
    # 策略说明
    report.append("## 📖 策略说明")
    report.append("")
    report.append("### 双均线交叉策略 (Dual Moving Average Crossover)")
    report.append("")
    report.append("**信号逻辑:**")
    report.append(f"- 🟢 **金叉买入**: 当 MA{results['parameters']['short_ma']} 上穿 MA{results['parameters']['long_ma']} 时，开多仓")
    report.append(f"- 🔴 **死叉卖出**: 当 MA{results['parameters']['short_ma']} 下穿 MA{results['parameters']['long_ma']} 时，平仓")
    report.append("")
    report.append("**策略特点:**")
    report.append("- 趋势跟踪策略，适合单边行情")
    report.append("- 震荡市场容易产生频繁交易和亏损")
    report.append("- 均线周期越长，信号越稳定但滞后性越大")
    report.append("")
    
    # 风险提示
    report.append("---")
    report.append("")
    report.append("⚠️ **风险提示**: 回测结果仅供参考，历史表现不代表未来收益。实盘交易请谨慎评估风险。")
    report.append("")
    
    return "\n".join(report)


def print_backtest_results(results: Dict[str, Any], trades_df: pd.DataFrame):
    """打印回测结果"""
    print()
    print("=" * 70)
    print("📊 双均线策略回测报告")
    print("=" * 70)
    
    print(f"\n📋 策略参数")
    print("-" * 40)
    print(f"  策略名称: {results['strategy_name']}")
    print(f"  短期均线: {results['parameters']['short_ma']} 日")
    print(f"  长期均线: {results['parameters']['long_ma']} 日")
    print(f"  数据周期: {results['data_start']} ~ {results['data_end']}")
    print(f"  数据点数: {results['data_points']}")
    
    print(f"\n💰 收益指标")
    print("-" * 40)
    print(f"  初始资金: ${results['initial_capital']:,.2f}")
    print(f"  最终资金: ${results['final_capital']:,.2f}")
    print(f"  总收益率: {results['total_return_pct']:+.2f}%")
    print(f"  年化收益: {results['annualized_return_pct']:+.2f}%")
    
    print(f"\n📉 风险指标")
    print("-" * 40)
    print(f"  夏普比率: {results['sharpe_ratio']:.3f}")
    print(f"  最大回撤: {results['max_drawdown_pct']:.2f}%")
    print(f"  波动率:   {results['volatility_pct']:.2f}%")
    
    print(f"\n🎯 交易统计")
    print("-" * 40)
    print(f"  总交易次数: {results['total_trades']}")
    print(f"  盈利次数:   {results['winning_trades']}")
    print(f"  亏损次数:   {results['losing_trades']}")
    print(f"  胜率:       {results['win_rate_pct']:.2f}%")
    print(f"  盈亏比:     {results['profit_factor']}")
    
    print(f"\n💵 盈亏统计")
    print("-" * 40)
    print(f"  平均盈利: ${results['avg_win']:,.2f}")
    print(f"  平均亏损: ${results['avg_loss']:,.2f}")
    print(f"  最大盈利: ${results['max_win']:,.2f}")
    print(f"  最大亏损: ${results['max_loss']:,.2f}")
    
    if not trades_df.empty:
        print(f"\n📝 交易记录 (最近 10 笔)")
        print("-" * 70)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        print(trades_df.tail(10).to_string(index=False))
    
    print()
    print("=" * 70)


# =============================================================================
# 主函数
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="双均线策略回测",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 默认参数回测 (使用 SDK 的 DataRetriever 获取数据)
  python dual_ma_backtest.py

  # 自定义均线参数
  python dual_ma_backtest.py --short-ma 10 --long-ma 50

  # 回测 ETH 一年数据
  python dual_ma_backtest.py --symbol ETH-USD --days 365

  # 导出 Markdown 报告
  python dual_ma_backtest.py --days 365 --report report.md
        """
    )
    
    # 数据参数
    parser.add_argument("--source", default="yahoo", 
                        choices=["yahoo", "1024ex", "binance"],
                        help="数据源 (默认: yahoo, 使用 SDK 的 DataRetriever)")
    parser.add_argument("--symbol", default="BTC-USD",
                        help="交易标的 (默认: BTC-USD, 1024ex使用BTC-PERP)")
    parser.add_argument("--config", type=str, default=None,
                        help="API 配置文件路径 (1024ex 数据源需要)")
    parser.add_argument("--interval", default="1d",
                        help="K线周期 (默认: 1d)")
    parser.add_argument("--days", type=int, default=180,
                        help="回测天数 (默认: 180)")
    
    # 策略参数
    parser.add_argument("--short-ma", type=int, default=5,
                        help="短期均线周期 (默认: 5)")
    parser.add_argument("--long-ma", type=int, default=20,
                        help="长期均线周期 (默认: 20)")
    parser.add_argument("--capital", type=float, default=10000,
                        help="初始资金 (默认: 10000)")
    parser.add_argument("--position-size", type=float, default=1.0,
                        help="仓位比例 0~1 (默认: 1.0)")
    parser.add_argument("--slippage", type=float, default=0.001,
                        help="滑点 (默认: 0.001 = 0.1%%)")
    parser.add_argument("--commission", type=float, default=0.001,
                        help="手续费 (默认: 0.001 = 0.1%%)")
    
    # 输出参数
    parser.add_argument("--plot", action="store_true",
                        help="显示图表")
    parser.add_argument("--output", type=str, default=None,
                        help="保存图表到文件")
    parser.add_argument("--export-trades", type=str, default=None,
                        help="导出交易记录到 CSV")
    parser.add_argument("--report", type=str, default=None,
                        help="导出 Markdown 报告到文件")
    parser.add_argument("--quiet", action="store_true",
                        help="静默模式，只输出统计结果")
    
    args = parser.parse_args()
    
    # 验证参数
    if args.short_ma >= args.long_ma:
        print("❌ 错误: 短期均线周期必须小于长期均线周期")
        return 1
    
    if not args.quiet:
        print()
        print("=" * 70)
        print("🚀 双均线策略回测 (Dual Moving Average Crossover)")
        print("=" * 70)
        print(f"  数据源: {args.source}")
        print(f"  标的:   {args.symbol}")
        print(f"  周期:   {args.interval}")
        print(f"  天数:   {args.days}")
        print(f"  均线:   MA{args.short_ma} / MA{args.long_ma}")
        print()
    
    # 获取数据
    try:
        if not args.quiet:
            print("📥 正在获取数据...")
        
        # 根据数据源准备参数
        retriever_kwargs = {
            "source": args.source,
            "enable_cache": True
        }
        
        # 1024ex 需要 API 配置
        if args.source == "1024ex":
            api_config = load_api_config(args.config)
            if api_config is None:
                print("❌ 错误: 1024ex 数据源需要 API 配置文件")
                print("   请在项目根目录创建 1024-trading-api-key-quant.json")
                print("   或使用 --config 参数指定配置文件路径")
                print("   或使用 --source yahoo 切换到 Yahoo Finance 数据源")
                return 1
            retriever_kwargs["api_key"] = api_config["api_key"]
            retriever_kwargs["api_secret"] = api_config["secret_key"]
        
        # 使用 SDK 的 DataRetriever 获取数据
        data_retriever = DataRetriever(**retriever_kwargs)
        data = data_retriever.get_klines(
            symbol=args.symbol,
            interval=args.interval,
            days=args.days,
            fill_missing=True,
            validate_data=True,
            add_indicators=False  # 我们自己计算均线
        )
        
        if len(data) < args.long_ma + 10:
            print(f"❌ 数据不足: 获取到 {len(data)} 条数据，需要至少 {args.long_ma + 10} 条")
            return 1
        
        if not args.quiet:
            print(f"✅ 获取到 {len(data)} 条数据")
            print(f"   时间范围: {data['timestamp'].iloc[0]} ~ {data['timestamp'].iloc[-1]}")
    
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        if args.source == "yahoo":
            print("   请安装: pip install yfinance")
        return 1
    except Exception as e:
        print(f"❌ 获取数据失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # 创建策略
    config = StrategyConfig(
        short_ma_period=args.short_ma,
        long_ma_period=args.long_ma,
        initial_capital=args.capital,
        position_size=args.position_size,
        slippage=args.slippage,
        commission=args.commission
    )
    strategy = DualMAStrategy(config)
    
    # 运行回测
    if not args.quiet:
        print("\n⚙️  正在运行回测...")
    
    engine = BacktestEngine(strategy, data)
    results = engine.run()
    trades_df = engine.get_trades_df()
    
    # 输出结果
    print_backtest_results(results, trades_df)
    
    # 导出交易记录
    if args.export_trades:
        trades_df.to_csv(args.export_trades, index=False, encoding='utf-8-sig')
        print(f"✅ 交易记录已导出到: {args.export_trades}")
    
    # 导出 Markdown 报告
    if args.report:
        report_content = generate_markdown_report(results, trades_df, engine, args)
        with open(args.report, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"✅ 回测报告已导出到: {args.report}")
    
    # 绘制图表
    if args.plot or args.output:
        engine.plot_results(save_path=args.output)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
