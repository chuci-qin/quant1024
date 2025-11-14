"""
Live Trading Module - Start trading with your strategy in one function call

让用户用最简单的方式开始实盘交易
"""

import time
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from .core import QuantStrategy
from .exchanges import BaseExchange, Exchange1024ex
from .exceptions import Quant1024Exception, InvalidParameterError
from .monitor_feeds import RuntimeConfig, RuntimeReporter


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LiveTrader:
    """
    实盘交易器 - 将策略应用到实盘交易
    
    核心功能：
    - 实时获取市场数据
    - 根据策略生成信号
    - 自动执行交易
    - 风险管理
    - 持仓监控
    
    设计说明：
    - 使用 BaseExchange 抽象接口，支持多个交易所
    - 只依赖 3 个核心方法：get_ticker, get_positions, place_order
    - 任何实现 BaseExchange 的交易所都可以使用
    """
    
    def __init__(
        self,
        strategy: QuantStrategy,
        exchange: BaseExchange,
        market: str,
        initial_capital: float,
        max_position_size: float = 1.0,
        check_interval: int = 60,
        max_slippage: float = 0.01,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        # ========== 简化：只有一个参数 ==========
        runtime_config: Optional[RuntimeConfig] = None
    ):
        """
        初始化实盘交易器
        
        Args:
            strategy: 交易策略（继承自 QuantStrategy）
            exchange: 交易所连接器（实现 BaseExchange 接口）
            market: 交易对（如 "BTC-PERP"）
            initial_capital: 初始资金
            max_position_size: 最大仓位比例（0-1，默认1.0=满仓）
            check_interval: 检查间隔（秒，默认60秒）
            max_slippage: 最大滑点容忍度（默认1%）
            stop_loss: 止损百分比（可选）
            take_profit: 止盈百分比（可选）
            runtime_config: Runtime 监控配置
                - 如果提供，自动启用监控
                - 如果为 None，不启用监控
        """
        self.strategy = strategy
        self.exchange = exchange
        self.market = market
        self.initial_capital = initial_capital
        self.max_position_size = max_position_size
        self.check_interval = check_interval
        self.max_slippage = max_slippage
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        
        # 运行状态
        self.is_running = False
        self.current_position = 0.0  # 当前持仓大小
        self.entry_price = 0.0       # 入场价格
        self.trades_count = 0         # 交易次数
        self.price_history = []       # 价格历史（用于生成信号）
        self.history_length = 100     # 保留的历史数据长度
        
        # ========== 简化：Runtime 监控 ==========
        self.runtime_config = runtime_config
        self.runtime_reporter: Optional[RuntimeReporter] = None
        
        if self.runtime_config:
            try:
                # 创建报告器（移除 exchange 参数）
                self.runtime_reporter = RuntimeReporter(self.runtime_config)
                
                # 创建 Runtime
                success = self.runtime_reporter.create_runtime(
                    market=market,
                    initial_capital=initial_capital,
                    max_position_size=max_position_size
                )
                
                if not success:
                    logger.warning(
                        "❌ 创建 Runtime 失败，监控功能已禁用，交易将继续进行"
                    )
                    self.runtime_reporter = None
            except Exception as e:
                logger.error(
                    f"❌ Runtime 初始化错误: {e}，"
                    f"监控功能已禁用，交易将继续进行"
                )
                self.runtime_reporter = None
        
        # 初始化策略
        if not strategy._is_initialized:
            strategy.initialize()
        
        logger.info(
            f"LiveTrader 初始化完成: "
            f"策略={strategy.name}, 市场={market}, "
            f"监控={'启用' if self.runtime_reporter else '禁用'}"
        )
    
    def start(self, max_iterations: Optional[int] = None):
        """
        开始实盘交易
        
        Args:
            max_iterations: 最大迭代次数（用于测试，None表示无限运行）
        """
        self.is_running = True
        iteration = 0
        
        logger.info("=" * 60)
        logger.info("🚀 开始实盘交易")
        logger.info(f"策略: {self.strategy.name}")
        logger.info(f"市场: {self.market}")
        logger.info(f"初始资金: ${self.initial_capital}")
        logger.info(f"检查间隔: {self.check_interval}秒")
        logger.info("=" * 60)
        
        try:
            while self.is_running:
                iteration += 1
                
                # 检查是否达到最大迭代次数
                if max_iterations and iteration > max_iterations:
                    logger.info(f"达到最大迭代次数 {max_iterations}，停止交易")
                    break
                
                # 执行一次交易循环
                self._trading_loop()
                
                # 等待下一次检查
                if self.is_running:
                    time.sleep(self.check_interval)
        
        except KeyboardInterrupt:
            logger.info("\n收到停止信号，正在安全退出...")
            self.stop()
        except Exception as e:
            logger.error(f"交易过程中发生错误: {e}", exc_info=True)
            self.stop()
    
    def stop(self):
        """停止交易"""
        self.is_running = False
        
        # 更新 Runtime 状态为 stopped
        if self.runtime_reporter:
            try:
                self.runtime_reporter.update_runtime_status(
                    "stopped",
                    total_trades=self.trades_count,
                    final_position=self.current_position
                )
            except Exception as e:
                logger.error(f"更新 Runtime 状态失败: {e}")
        
        logger.info("=" * 60)
        logger.info("🛑 交易已停止")
        logger.info(f"总交易次数: {self.trades_count}")
        logger.info(f"当前持仓: {self.current_position}")
        logger.info("=" * 60)
    
    def _trading_loop(self):
        """单次交易循环"""
        try:
            # 1. 获取最新市场数据
            current_price = self._get_current_price()
            if current_price is None:
                logger.warning("无法获取当前价格，跳过本次循环")
                return
            
            # 2. 更新价格历史
            self._update_price_history(current_price)
            
            # 3. 检查是否有足够的历史数据
            if len(self.price_history) < 10:  # 至少需要10个数据点
                logger.info(f"正在积累历史数据... ({len(self.price_history)}/10)")
                return
            
            # 4. 生成交易信号
            signal = self._generate_signal()
            
            # 5. 获取当前实际持仓
            actual_position = self._get_current_position_from_exchange()
            
            # 6. 检查止损止盈
            if self._check_stop_loss_take_profit(current_price):
                return
            
            # 7. 计算目标仓位
            target_position = self.strategy.calculate_position(signal, actual_position)
            target_position = min(target_position, self.max_position_size)
            
            # 8. 执行交易
            if abs(target_position - actual_position) > 0.001:  # 仓位变化超过0.1%才交易
                self._execute_trade(target_position, actual_position, current_price)
            
            # 9. 报告信号到监控系统
            if self.runtime_reporter:
                try:
                    self.runtime_reporter.report_signal(
                        market=self.market,
                        signal=signal,
                        price=current_price,
                        current_position=actual_position,
                        target_position=target_position
                    )
                except Exception as e:
                    logger.error(f"报告信号失败: {e}")
            
            # 10. 记录状态
            logger.info(
                f"📊 状态 | 价格: ${current_price:.2f} | "
                f"信号: {self._signal_to_str(signal)} | "
                f"当前仓位: {actual_position:.4f} | "
                f"目标仓位: {target_position:.4f}"
            )
        
        except Exception as e:
            logger.error(f"交易循环错误: {e}", exc_info=True)
    
    def _get_current_price(self) -> Optional[float]:
        """获取当前价格"""
        try:
            ticker = self.exchange.get_ticker(self.market)
            # 处理不同的响应格式
            if isinstance(ticker, dict):
                # 如果有 'data' 字段，从 data 中获取
                if 'data' in ticker:
                    data = ticker['data']
                    price = float(data.get('last_price', 0))
                else:
                    # 直接从ticker获取
                    price = float(ticker.get('last_price', 0))
            else:
                price = 0
            return price if price > 0 else None
        except Exception as e:
            logger.error(f"获取价格失败: {e}", exc_info=True)
            return None
    
    def _update_price_history(self, price: float):
        """更新价格历史"""
        self.price_history.append(price)
        
        # 只保留最近的 N 个数据点
        if len(self.price_history) > self.history_length:
            self.price_history.pop(0)
    
    def _generate_signal(self) -> int:
        """生成交易信号"""
        try:
            signals = self.strategy.generate_signals(self.price_history)
            return signals[-1] if signals else 0
        except Exception as e:
            logger.error(f"生成信号失败: {e}")
            return 0
    
    def _get_current_position_from_exchange(self) -> float:
        """从交易所获取当前持仓"""
        try:
            positions = self.exchange.get_positions(market=self.market)
            # 处理不同的响应格式
            if isinstance(positions, dict):
                # 如果有 'data' 字段，从 data 中获取
                if 'data' in positions:
                    positions = positions['data']
            
            if positions and len(positions) > 0:
                position_size = float(positions[0].get('size', 0))
                self.current_position = position_size
                return position_size
            return 0.0
        except Exception as e:
            logger.error(f"获取持仓失败: {e}", exc_info=True)
            return self.current_position
    
    def _check_stop_loss_take_profit(self, current_price: float) -> bool:
        """检查止损止盈"""
        if self.current_position == 0 or self.entry_price == 0:
            return False
        
        pnl_pct = (current_price - self.entry_price) / self.entry_price
        
        # 止损
        if self.stop_loss and pnl_pct <= -self.stop_loss:
            logger.warning(f"🛑 触发止损! 当前亏损: {pnl_pct*100:.2f}%")
            self._close_position(current_price, "止损")
            return True
        
        # 止盈
        if self.take_profit and pnl_pct >= self.take_profit:
            logger.info(f"🎯 触发止盈! 当前盈利: {pnl_pct*100:.2f}%")
            self._close_position(current_price, "止盈")
            return True
        
        return False
    
    def _execute_trade(self, target_position: float, current_position: float, current_price: float):
        """执行交易"""
        try:
            position_diff = target_position - current_position
            
            if abs(position_diff) < 0.001:
                return
            
            # 计算交易方向和数量
            side = "buy" if position_diff > 0 else "sell"
            size = abs(position_diff)
            
            # 计算订单金额
            order_value = size * current_price
            
            # 风险检查
            if order_value > self.initial_capital * self.max_position_size:
                logger.warning(f"订单金额超出限制，跳过交易")
                return
            
            # 下市价单
            logger.info(f"📝 执行交易: {side.upper()} {size:.4f} @ ${current_price:.2f}")
            
            order = self.exchange.place_order(
                market=self.market,
                side=side,
                order_type="market",  # 使用市价单快速成交
                size=str(size)
            )
            
            # 更新状态
            self.current_position = target_position
            self.trades_count += 1
            
            if target_position > 0 and current_position == 0:
                self.entry_price = current_price
            elif target_position == 0:
                self.entry_price = 0
            
            # 报告交易到监控系统
            if self.runtime_reporter:
                try:
                    self.runtime_reporter.report_trade(
                        market=self.market,
                        side=side,
                        size=size,
                        price=current_price,
                        order_id=order.get('order_id'),
                        position_before=current_position,
                        position_after=target_position
                    )
                    
                    # 报告持仓更新
                    self.runtime_reporter.report_position(
                        market=self.market,
                        position_size=self.current_position,
                        entry_price=self.entry_price,
                        current_price=current_price
                    )
                except Exception as e:
                    logger.error(f"报告交易/持仓失败: {e}")
            
            logger.info(f"✅ 交易成功! 订单ID: {order.get('order_id', 'N/A')}")
        
        except Exception as e:
            logger.error(f"执行交易失败: {e}", exc_info=True)
    
    def _close_position(self, current_price: float, reason: str):
        """平仓"""
        try:
            if self.current_position == 0:
                return
            
            logger.info(f"平仓原因: {reason}")
            self._execute_trade(0.0, self.current_position, current_price)
        except Exception as e:
            logger.error(f"平仓失败: {e}")
    
    def _signal_to_str(self, signal: int) -> str:
        """信号转字符串"""
        if signal == 1:
            return "🟢 BUY"
        elif signal == -1:
            return "🔴 SELL"
        else:
            return "⚪ HOLD"
    
    def get_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            "is_running": self.is_running,
            "strategy": self.strategy.name,
            "market": self.market,
            "current_position": self.current_position,
            "entry_price": self.entry_price,
            "trades_count": self.trades_count,
            "price_history_length": len(self.price_history)
        }


def start_trading(
    strategy: QuantStrategy,
    api_key: str,
    api_secret: str,
    market: str,
    initial_capital: float = 10000,
    exchange: str = "1024ex",
    base_url: str = "https://api.1024ex.com",
    max_position_size: float = 0.5,
    check_interval: int = 60,
    stop_loss: Optional[float] = 0.05,
    take_profit: Optional[float] = 0.10,
    # ========== 简化：只有一个参数 ==========
    runtime_config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> LiveTrader:
    """
    🚀 开始实盘交易 - 一行代码启动你的交易策略！
    
    这是最简单的方式来开始实盘交易。只需要传入你的策略和API密钥即可。
    
    Args:
        strategy: 你的交易策略（继承自 QuantStrategy）
        api_key: API Key（交易所）
        api_secret: API Secret（交易所）
        market: 交易市场（如 "BTC-PERP"）
        initial_capital: 初始资金（默认 10000）
        exchange: 交易所名称（默认 "1024ex"）
        base_url: API 地址（默认 1024ex 主网）
        max_position_size: 最大仓位比例 0-1（默认 0.5 = 50%仓位）
        check_interval: 检查间隔秒数（默认 60秒）
        stop_loss: 止损比例（默认 0.05 = 5%）
        take_profit: 止盈比例（默认 0.10 = 10%）
        runtime_config: Runtime 监控配置字典（可选）
            - 必填: "api_key"
            - 可选: "api_base_url", "strategy_id", "environment", "metadata"
            - runtime_id 会自动生成（UUID）
            - 如果不提供，不启用监控
        **kwargs: 其他参数
    
    Returns:
        LiveTrader 实例
    
    Example 1 - 基本使用（不启用监控）:
        ```python
        from quant1024 import QuantStrategy, start_trading
        
        class MyStrategy(QuantStrategy):
            def generate_signals(self, data):
                if len(data) < 2:
                    return [0]
                return [1 if data[-1] > data[-2] else -1]
            
            def calculate_position(self, signal, current_position):
                if signal == 1:
                    return 1.0
                elif signal == -1:
                    return 0.0
                return current_position
        
        # 开始交易！
        trader = start_trading(
            strategy=MyStrategy(name="趋势策略"),
            api_key="your_api_key",
            api_secret="your_api_secret",
            market="BTC-PERP",
            initial_capital=10000
        )
        ```
    
    Example 2 - 启用监控（最简单）:
        ```python
        trader = start_trading(
            strategy=MyStrategy(name="策略"),
            api_key="exchange_api_key",
            api_secret="exchange_api_secret",
            market="BTC-PERP",
            runtime_config={
                "api_key": "server_api_key"  # 只需这一个！
            }
        )
        ```
    
    Example 3 - 完整配置:
        ```python
        trader = start_trading(
            strategy=MyStrategy(name="策略"),
            api_key="exchange_api_key",
            api_secret="exchange_api_secret",
            market="BTC-PERP",
            runtime_config={
                "api_key": "server_api_key",
                "api_base_url": "https://custom-api.com",
                "strategy_id": "uuid",
                "environment": "production",
                "metadata": {"version": "1.0"}
                # runtime_id 会自动生成，无需手动指定
            }
        )
        ```
    
    Raises:
        InvalidParameterError: 参数错误
        Quant1024Exception: 其他错误
    """
    
    # 参数验证
    if not isinstance(strategy, QuantStrategy):
        raise InvalidParameterError("strategy 必须是 QuantStrategy 的子类")
    
    if not api_key or not api_secret:
        raise InvalidParameterError("api_key 和 api_secret 不能为空")
    
    if initial_capital <= 0:
        raise InvalidParameterError("initial_capital 必须大于 0")
    
    if not 0 < max_position_size <= 1:
        raise InvalidParameterError("max_position_size 必须在 0-1 之间")
    
    # ========== 简化：处理 runtime_config ==========
    runtime_config_obj = None
    if runtime_config:
        try:
            # 验证必填字段
            if not runtime_config.get('api_key'):
                logger.error(
                    "❌ Runtime config 错误: 缺少必填字段 'api_key'，"
                    "监控功能已禁用，交易将继续进行"
                )
            else:
                # 创建 RuntimeConfig 对象
                runtime_config_obj = RuntimeConfig(
                    api_key=runtime_config['api_key'],
                    runtime_id=str(__import__('uuid').uuid4()),  # 自动生成 UUID
                    strategy_id=runtime_config.get('strategy_id'),
                    api_base_url=runtime_config.get(
                        'api_base_url',
                        'https://api.1024quant.com'  # 默认：1024Quant 平台 API
                    ),
                    environment=runtime_config.get('environment'),
                    extra_metadata=runtime_config.get('metadata')
                )
        except Exception as e:
            logger.error(
                f"❌ Runtime config 配置错误: {e}，"
                f"监控功能已禁用，交易将继续进行"
            )
            runtime_config_obj = None
    
    # 创建交易所连接
    if exchange.lower() == "1024ex":
        exchange_client = Exchange1024ex(
            api_key=api_key,
            api_secret=api_secret,
            base_url=base_url
        )
    else:
        raise InvalidParameterError(f"暂不支持交易所: {exchange}")
    
    # 创建交易器
    trader = LiveTrader(
        strategy=strategy,
        exchange=exchange_client,
        market=market,
        initial_capital=initial_capital,
        max_position_size=max_position_size,
        check_interval=check_interval,
        stop_loss=stop_loss,
        take_profit=take_profit,
        # ========== 简化：只传一个参数 ==========
        runtime_config=runtime_config_obj
    )
    
    # 开始交易
    try:
        trader.start()
    except KeyboardInterrupt:
        logger.info("用户中断交易")
        trader.stop()
    
    return trader

