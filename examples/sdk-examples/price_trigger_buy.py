#!/usr/bin/env python3
"""
价格触发自动购买脚本

当价格到达设定的目标价格时，自动执行买入操作。

功能特点:
- 支持永续合约 (perp) 和现货 (spot) 交易
- 支持两种触发模式: 跌破买入 / 涨破买入
- 支持限价单 / 市价单
- 实时价格监控和日志输出
- 优雅的中断处理 (Ctrl+C)

使用方法:
    # 基本使用 - 当 BTC 跌到 90000 时市价买入 0.01
    python price_trigger_buy.py --market BTC-USDC --trigger-price 90000 --size 0.01

    # 跌破买入 + 限价单
    python price_trigger_buy.py --market BTC-USDC --trigger-price 90000 --size 0.01 --order-price 89500

    # 涨破买入 (价格超过目标时买入)
    python price_trigger_buy.py --market ETH-USDC --trigger-price 4000 --size 0.1 --direction up

    # 使用现货交易
    python price_trigger_buy.py --market SOL-USDC --trigger-price 180 --size 5 --mode spot

    # Dry-run 模式 (不实际下单)
    python price_trigger_buy.py --market BTC-USDC --trigger-price 90000 --size 0.01 --dry-run

环境变量:
    DRY_RUN: 设置为 "true" 启用模拟模式
"""

import argparse
import json
import os
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from quant1024 import Exchange1024ex
from quant1024 import Quant1024Exception, APIError


# =============================================================================
# 配置
# =============================================================================

# 默认监控间隔 (秒)
DEFAULT_CHECK_INTERVAL = 2.0

# 默认杠杆 (永续合约)
DEFAULT_LEVERAGE = 1


# =============================================================================
# 配置加载
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
        raise FileNotFoundError(f"配置文件不存在: {config_path}\n"
                                f"请创建配置文件，格式参考 README.md")
    
    with open(config_path, "r") as f:
        config = json.load(f)
    
    # 验证必要字段
    required_fields = ["api_key", "secret_key"]
    for field in required_fields:
        if field not in config:
            raise ValueError(f"配置文件缺少必要字段: {field}")
    
    return config


# =============================================================================
# 价格触发器
# =============================================================================

class PriceTriggerBot:
    """
    价格触发自动购买机器人
    """
    
    def __init__(
        self,
        exchange: Exchange1024ex,
        market: str,
        trigger_price: float,
        size: str,
        direction: str = "down",        # "down" 跌破买入, "up" 涨破买入
        order_price: Optional[str] = None,  # None 则市价单
        mode: str = "perp",              # "perp" 或 "spot"
        leverage: int = DEFAULT_LEVERAGE,
        check_interval: float = DEFAULT_CHECK_INTERVAL,
        dry_run: bool = False
    ):
        self.exchange = exchange
        self.market = market
        self.trigger_price = trigger_price
        self.size = size
        self.direction = direction
        self.order_price = order_price
        self.mode = mode
        self.leverage = leverage
        self.check_interval = check_interval
        self.dry_run = dry_run
        
        self.running = False
        self.triggered = False
        self.last_price: Optional[float] = None
        
    def _log(self, message: str, level: str = "INFO"):
        """输出日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        icons = {
            "INFO": "📊",
            "WARN": "⚠️ ",
            "ERROR": "❌",
            "OK": "✅",
            "TRIGGER": "🎯",
            "ORDER": "📝"
        }
        icon = icons.get(level, "  ")
        print(f"[{timestamp}] {icon} {message}")
    
    def get_current_price(self) -> Optional[float]:
        """获取当前价格"""
        try:
            if self.mode == "perp":
                ticker = self.exchange.perp.get_ticker(self.market)
            else:
                ticker = self.exchange.spot.get_ticker(self.market)
            
            # 解析价格 - API 返回格式可能不同
            if isinstance(ticker, dict):
                data = ticker.get("data", ticker)
                price = data.get("last_price") or data.get("lastPrice") or data.get("price")
                if price:
                    return float(price)
            return None
        except Exception as e:
            self._log(f"获取价格失败: {e}", "ERROR")
            return None
    
    def check_trigger(self, current_price: float) -> bool:
        """检查是否触发条件"""
        if self.direction == "down":
            # 跌破买入: 当前价格 <= 触发价格
            return current_price <= self.trigger_price
        else:
            # 涨破买入: 当前价格 >= 触发价格
            return current_price >= self.trigger_price
    
    def place_order(self) -> Dict[str, Any]:
        """执行下单"""
        order_type = "limit" if self.order_price else "market"
        
        self._log(f"触发条件满足! 准备下单...", "TRIGGER")
        self._log(f"  市场: {self.market}", "ORDER")
        self._log(f"  方向: long (买入)", "ORDER")
        self._log(f"  类型: {order_type}", "ORDER")
        self._log(f"  数量: {self.size}", "ORDER")
        if self.order_price:
            self._log(f"  价格: {self.order_price}", "ORDER")
        if self.mode == "perp":
            self._log(f"  杠杆: {self.leverage}x", "ORDER")
        
        if self.dry_run:
            self._log("🔸 Dry-run 模式，跳过实际下单", "WARN")
            return {"success": True, "dry_run": True, "message": "模拟下单成功"}
        
        try:
            if self.mode == "perp":
                result = self.exchange.perp.place_order(
                    market=self.market,
                    side="long",
                    order_type=order_type,
                    size=self.size,
                    price=self.order_price,
                    leverage=self.leverage
                )
            else:
                result = self.exchange.spot.place_order(
                    market=self.market,
                    side="buy",
                    order_type=order_type,
                    size=self.size,
                    price=self.order_price
                )
            
            self._log(f"下单成功!", "OK")
            self._log(f"  响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
            return result
            
        except Exception as e:
            self._log(f"下单失败: {e}", "ERROR")
            return {"success": False, "error": str(e)}
    
    def run(self):
        """运行价格监控循环"""
        self.running = True
        
        mode_text = "永续合约" if self.mode == "perp" else "现货"
        direction_text = "跌破" if self.direction == "down" else "涨破"
        order_type = "限价单" if self.order_price else "市价单"
        dry_run_text = " [DRY-RUN]" if self.dry_run else ""
        
        print()
        print("=" * 60)
        print(f"🤖 价格触发自动购买机器人{dry_run_text}")
        print("=" * 60)
        print(f"  市场: {self.market} ({mode_text})")
        print(f"  触发价格: {self.trigger_price} ({direction_text}买入)")
        print(f"  购买数量: {self.size}")
        print(f"  订单类型: {order_type}" + (f" @ {self.order_price}" if self.order_price else ""))
        if self.mode == "perp":
            print(f"  杠杆倍数: {self.leverage}x")
        print(f"  检查间隔: {self.check_interval} 秒")
        print("=" * 60)
        print("按 Ctrl+C 停止监控")
        print()
        
        check_count = 0
        
        while self.running and not self.triggered:
            try:
                current_price = self.get_current_price()
                
                if current_price is None:
                    self._log(f"无法获取价格，{self.check_interval}秒后重试...", "WARN")
                    time.sleep(self.check_interval)
                    continue
                
                self.last_price = current_price
                check_count += 1
                
                # 计算价格差距
                if self.direction == "down":
                    diff = current_price - self.trigger_price
                    diff_pct = (diff / self.trigger_price) * 100
                    status = f"距触发: {diff:.2f} ({diff_pct:+.2f}%)"
                else:
                    diff = self.trigger_price - current_price
                    diff_pct = (diff / self.trigger_price) * 100
                    status = f"距触发: {diff:.2f} ({diff_pct:+.2f}%)"
                
                # 检查触发条件
                if self.check_trigger(current_price):
                    self._log(f"当前价格: {current_price:.4f} - 触发!", "TRIGGER")
                    self.triggered = True
                    result = self.place_order()
                    
                    if result.get("success") or result.get("dry_run"):
                        self._log("任务完成，退出监控", "OK")
                    else:
                        self._log("下单失败，退出监控", "ERROR")
                    break
                else:
                    self._log(f"当前价格: {current_price:.4f} | {status}")
                
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self._log(f"监控异常: {e}", "ERROR")
                time.sleep(self.check_interval)
        
        if not self.triggered:
            print()
            self._log(f"监控已停止，共检查 {check_count} 次", "INFO")
    
    def stop(self):
        """停止监控"""
        self.running = False


# =============================================================================
# 主函数
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="价格触发自动购买脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 当 BTC 跌到 90000 时市价买入 0.01 BTC
  python price_trigger_buy.py --market BTC-USDC --trigger-price 90000 --size 0.01

  # 当 BTC 跌到 90000 时，以 89500 限价买入 0.01 BTC
  python price_trigger_buy.py --market BTC-USDC --trigger-price 90000 --size 0.01 --order-price 89500

  # 当 ETH 涨到 4000 时买入 (追涨)
  python price_trigger_buy.py --market ETH-USDC --trigger-price 4000 --size 0.1 --direction up

  # 现货交易
  python price_trigger_buy.py --market SOL-USDC --trigger-price 180 --size 5 --mode spot

  # 模拟运行 (不下单)
  python price_trigger_buy.py --market BTC-USDC --trigger-price 90000 --size 0.01 --dry-run
        """
    )
    
    parser.add_argument("--market", required=True, help="交易市场，如 BTC-USDC")
    parser.add_argument("--trigger-price", type=float, required=True, help="触发价格")
    parser.add_argument("--size", required=True, help="购买数量")
    parser.add_argument("--order-price", type=str, default=None, help="下单价格 (不填则市价单)")
    parser.add_argument("--direction", choices=["down", "up"], default="down",
                        help="触发方向: down=跌破买入, up=涨破买入 (默认: down)")
    parser.add_argument("--mode", choices=["perp", "spot"], default="perp",
                        help="交易模式: perp=永续合约, spot=现货 (默认: perp)")
    parser.add_argument("--leverage", type=int, default=DEFAULT_LEVERAGE,
                        help=f"杠杆倍数，仅永续合约 (默认: {DEFAULT_LEVERAGE})")
    parser.add_argument("--interval", type=float, default=DEFAULT_CHECK_INTERVAL,
                        help=f"价格检查间隔秒数 (默认: {DEFAULT_CHECK_INTERVAL})")
    parser.add_argument("--config", type=str, default=None, help="API 配置文件路径")
    parser.add_argument("--base-url", type=str, default="https://api.1024ex.com",
                        help="API 基础 URL (默认: https://api.1024ex.com)")
    parser.add_argument("--dry-run", action="store_true", help="模拟运行，不实际下单")
    
    args = parser.parse_args()
    
    # 检查环境变量 DRY_RUN
    dry_run = args.dry_run or os.getenv("DRY_RUN", "").lower() == "true"
    
    # 加载配置
    try:
        config = load_api_config(args.config)
    except Exception as e:
        print(f"❌ 加载配置失败: {e}")
        return 1
    
    # 初始化 SDK
    exchange = Exchange1024ex(
        api_key=config["api_key"],
        secret_key=config["secret_key"],
        base_url=args.base_url
    )
    
    # 创建机器人
    bot = PriceTriggerBot(
        exchange=exchange,
        market=args.market,
        trigger_price=args.trigger_price,
        size=args.size,
        direction=args.direction,
        order_price=args.order_price,
        mode=args.mode,
        leverage=args.leverage,
        check_interval=args.interval,
        dry_run=dry_run
    )
    
    # 设置信号处理
    def signal_handler(signum, frame):
        print("\n")
        bot.stop()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 运行
    try:
        bot.run()
    except Exception as e:
        print(f"❌ 运行异常: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
