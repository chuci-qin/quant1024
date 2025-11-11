"""
Monitor Feeds - 使用示例

这个文件展示了如何使用 Runtime 监控功能
"""

from quant1024 import QuantStrategy, start_trading


# ============================================================
# 定义一个简单的策略
# ============================================================

class SimpleStrategy(QuantStrategy):
    """简单的趋势跟踪策略"""
    
    def generate_signals(self, data):
        """生成交易信号"""
        if len(data) < 2:
            return [0]
        
        # 简单的价格趋势判断
        if data[-1] > data[-2]:
            return [1]  # 上涨 -> 买入信号
        else:
            return [-1]  # 下跌 -> 卖出信号
    
    def calculate_position(self, signal, current_position):
        """计算目标仓位"""
        if signal == 1:
            return 1.0  # 做多满仓
        elif signal == -1:
            return 0.0  # 平仓
        return current_position  # 保持当前仓位


# ============================================================
# 示例 1: 最简单的使用（只需一个 api_key）
# ============================================================

def example_1_basic():
    """最简单的使用方式"""
    print("=" * 60)
    print("示例 1: 最简单的使用")
    print("=" * 60)
    
    trader = start_trading(
        strategy=SimpleStrategy(name="简单策略"),
        api_key="your_exchange_api_key",
        api_secret="your_exchange_api_secret",
        market="BTC-PERP",
        initial_capital=10000,
        
        # ✨ 只需这一个参数启用监控！
        runtime_config={
            "api_key": "your_server_api_key"  # 记录服务的 API Key
        }
    )
    
    # 自动行为：
    # - runtime_id: 自动生成 UUID
    # - strategy_id: 从环境变量 STRATEGY_ID 读取
    # - api_base_url: 默认 https://api.1024ex.com
    # - environment: 从环境变量 ENVIRONMENT 读取，默认 "local"


# ============================================================
# 示例 2: 完整配置
# ============================================================

def example_2_full_config():
    """完整配置示例"""
    print("=" * 60)
    print("示例 2: 完整配置")
    print("=" * 60)
    
    trader = start_trading(
        strategy=SimpleStrategy(name="完整配置策略"),
        api_key="your_exchange_api_key",
        api_secret="your_exchange_api_secret",
        market="BTC-PERP",
        initial_capital=10000,
        
        runtime_config={
            "api_key": "your_server_api_key",           # 必填
            "api_base_url": "https://custom-api.com",   # 可选，自定义记录服务
            "runtime_id": "custom-runtime-id-123",      # 可选，自定义 runtime ID
            "strategy_id": "strategy-uuid-456",         # 可选，策略 ID
            "environment": "production",                # 可选，运行环境
            "metadata": {                               # 可选，额外元数据
                "version": "1.0.0",
                "description": "生产环境策略",
                "git_commit": "abc123"
            }
        }
    )


# ============================================================
# 示例 3: 不启用监控
# ============================================================

def example_3_no_monitoring():
    """不启用监控的示例"""
    print("=" * 60)
    print("示例 3: 不启用监控")
    print("=" * 60)
    
    # 不传 runtime_config，不启用监控
    trader = start_trading(
        strategy=SimpleStrategy(name="无监控策略"),
        api_key="your_exchange_api_key",
        api_secret="your_exchange_api_secret",
        market="BTC-PERP",
        initial_capital=10000
        # runtime_config=None (默认)
    )


# ============================================================
# 示例 4: 使用环境变量
# ============================================================

def example_4_env_vars():
    """使用环境变量的示例"""
    print("=" * 60)
    print("示例 4: 使用环境变量")
    print("=" * 60)
    
    # 在运行前设置环境变量：
    # export STRATEGY_ID="my-strategy-uuid"
    # export ENVIRONMENT="production"
    # export API_BASE_URL="https://custom-api.com"  # 可选
    
    trader = start_trading(
        strategy=SimpleStrategy(name="环境变量策略"),
        api_key="your_exchange_api_key",
        api_secret="your_exchange_api_secret",
        market="BTC-PERP",
        initial_capital=10000,
        
        runtime_config={
            "api_key": "your_server_api_key"
            # strategy_id 和 environment 会从环境变量读取
        }
    )


# ============================================================
# 示例 5: 直接使用 RuntimeReporter
# ============================================================

def example_5_direct_usage():
    """直接使用 RuntimeReporter 的示例"""
    print("=" * 60)
    print("示例 5: 直接使用 RuntimeReporter")
    print("=" * 60)
    
    from quant1024.monitor_feeds import RuntimeConfig, RuntimeReporter
    
    # 创建配置
    config = RuntimeConfig(
        api_key="your_server_api_key",
        api_base_url="https://api.1024ex.com"
    )
    
    # 创建报告器
    reporter = RuntimeReporter(config)
    
    # 创建 Runtime
    success = reporter.create_runtime(
        market="BTC-PERP",
        initial_capital=10000,
        max_position_size=0.5
    )
    
    if success:
        # 报告交易
        reporter.report_trade(
            market="BTC-PERP",
            side="buy",
            size=0.1,
            price=50000,
            order_id="order-123"
        )
        
        # 报告信号
        reporter.report_signal(
            market="BTC-PERP",
            signal=1,  # 1=buy, -1=sell, 0=hold
            price=50000
        )
        
        # 报告持仓
        reporter.report_position(
            market="BTC-PERP",
            position_size=0.1,
            entry_price=50000,
            current_price=51000
        )
        
        # 更新状态
        reporter.update_runtime_status(
            "stopped",
            total_trades=10,
            final_position=0.0
        )


# ============================================================
# 主函数
# ============================================================

if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "Monitor Feeds - 使用示例" + " " * 23 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    print("请根据你的需求选择一个示例运行：")
    print()
    print("1. example_1_basic()         - 最简单的使用")
    print("2. example_2_full_config()   - 完整配置")
    print("3. example_3_no_monitoring() - 不启用监控")
    print("4. example_4_env_vars()      - 使用环境变量")
    print("5. example_5_direct_usage()  - 直接使用 RuntimeReporter")
    print()
    print("注意：请先配置正确的 API Keys 再运行！")
    print()
    
    # 取消注释以运行示例：
    # example_1_basic()
    # example_2_full_config()
    # example_3_no_monitoring()
    # example_4_env_vars()
    # example_5_direct_usage()

