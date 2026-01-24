#!/usr/bin/env python3
"""
quant1024 SDK 模块接口测试脚本

测试 /src/quant1024/exchanges/modules 下的所有模块是否能正确导入和使用。
包括: PerpModule, SpotModule, PredictionModule, ChampionshipModule, AccountModule

使用方法:
    python test_sdk_modules.py
"""

import sys
from typing import List, Tuple


def test_basic_import() -> Tuple[bool, str]:
    """测试基础导入"""
    try:
        import quant1024
        return True, f"✅ quant1024 版本: {quant1024.__version__}"
    except ImportError as e:
        return False, f"❌ 导入 quant1024 失败: {e}"


def test_module_imports() -> List[Tuple[str, bool, str]]:
    """测试所有模块的导入"""
    results = []
    
    # 测试从顶层导入模块类
    modules_to_test = [
        ("PerpModule", "from quant1024 import PerpModule"),
        ("SpotModule", "from quant1024 import SpotModule"),
        ("PredictionModule", "from quant1024 import PredictionModule"),
        ("ChampionshipModule", "from quant1024 import ChampionshipModule"),
        ("AccountModule", "from quant1024 import AccountModule"),
    ]
    
    for name, import_stmt in modules_to_test:
        try:
            exec(import_stmt)
            results.append((name, True, f"✅ {name} 导入成功"))
        except ImportError as e:
            results.append((name, False, f"❌ {name} 导入失败: {e}"))
    
    return results


def test_exchange_import() -> Tuple[bool, str]:
    """测试 Exchange1024ex 导入"""
    try:
        from quant1024 import Exchange1024ex
        return True, "✅ Exchange1024ex 导入成功"
    except ImportError as e:
        return False, f"❌ Exchange1024ex 导入失败: {e}"


def test_interface_imports() -> List[Tuple[str, bool, str]]:
    """测试接口导入"""
    results = []
    
    interfaces = [
        ("IMarketData", "from quant1024 import IMarketData"),
        ("ITrading", "from quant1024 import ITrading"),
        ("IPositions", "from quant1024 import IPositions"),
        ("IAdvancedOrders", "from quant1024 import IAdvancedOrders"),
    ]
    
    for name, import_stmt in interfaces:
        try:
            exec(import_stmt)
            results.append((name, True, f"✅ {name} 接口导入成功"))
        except ImportError as e:
            results.append((name, False, f"❌ {name} 接口导入失败: {e}"))
    
    return results


def test_exchange_creation() -> Tuple[bool, str]:
    """测试 Exchange1024ex 实例化"""
    try:
        from quant1024 import Exchange1024ex
        
        # 创建客户端实例（不需要真实 API Key）
        exchange = Exchange1024ex(
            api_key="test_api_key",
            secret_key="test_secret_key",
            base_url="https://api.1024ex.com"
        )
        
        return True, "✅ Exchange1024ex 实例化成功"
    except Exception as e:
        return False, f"❌ Exchange1024ex 实例化失败: {e}"


def test_module_access() -> List[Tuple[str, bool, str]]:
    """测试通过 exchange 访问各个模块"""
    results = []
    
    try:
        from quant1024 import Exchange1024ex
        exchange = Exchange1024ex(api_key="test", secret_key="test")
        
        # 测试各模块的属性访问
        modules = [
            ("exchange.perp", "PerpModule"),
            ("exchange.spot", "SpotModule"),
            ("exchange.prediction", "PredictionModule"),
            ("exchange.championship", "ChampionshipModule"),
            ("exchange.account", "AccountModule"),
        ]
        
        for attr_path, expected_class in modules:
            try:
                module = eval(attr_path)
                class_name = module.__class__.__name__
                if class_name == expected_class:
                    results.append((attr_path, True, f"✅ {attr_path} -> {class_name}"))
                else:
                    results.append((attr_path, False, f"❌ {attr_path} 类型错误: 期望 {expected_class}, 实际 {class_name}"))
            except Exception as e:
                results.append((attr_path, False, f"❌ {attr_path} 访问失败: {e}"))
                
    except Exception as e:
        results.append(("模块访问测试", False, f"❌ 初始化失败: {e}"))
    
    return results


def test_perp_module_methods() -> List[Tuple[str, bool, str]]:
    """测试 PerpModule 的方法是否存在"""
    results = []
    
    try:
        from quant1024 import Exchange1024ex
        exchange = Exchange1024ex(api_key="test", secret_key="test")
        perp = exchange.perp
        
        # 检查核心方法是否存在
        core_methods = [
            "get_markets",
            "get_ticker",
            "get_orderbook",
            "get_trades",
            "get_klines",
            "get_funding_rate",
            "place_order",
            "cancel_order",
            "get_orders",
            "get_positions",
            "set_leverage",
            "set_tpsl",
            "create_twap",
            "create_vwap",
            "create_oco",
            "create_bracket",
            "create_iceberg",
            "create_conditional",
            "create_scale",
            "create_trailing_stop",
            "create_pegged",
            "create_pov",
            "create_sniper",
        ]
        
        for method_name in core_methods:
            if hasattr(perp, method_name) and callable(getattr(perp, method_name)):
                results.append((f"perp.{method_name}", True, f"✅ perp.{method_name}() 存在"))
            else:
                results.append((f"perp.{method_name}", False, f"❌ perp.{method_name}() 不存在"))
                
    except Exception as e:
        results.append(("PerpModule 方法测试", False, f"❌ 测试失败: {e}"))
    
    return results


def test_spot_module_methods() -> List[Tuple[str, bool, str]]:
    """测试 SpotModule 的方法是否存在"""
    results = []
    
    try:
        from quant1024 import Exchange1024ex
        exchange = Exchange1024ex(api_key="test", secret_key="test")
        spot = exchange.spot
        
        core_methods = [
            "get_markets",
            "get_ticker",
            "get_balances",
            "place_order",
            "cancel_order",
            "get_orders",
            "create_conditional",
            "create_twap",
            "create_vwap",
            "create_oco",
            "create_iceberg",
        ]
        
        for method_name in core_methods:
            if hasattr(spot, method_name) and callable(getattr(spot, method_name)):
                results.append((f"spot.{method_name}", True, f"✅ spot.{method_name}() 存在"))
            else:
                results.append((f"spot.{method_name}", False, f"❌ spot.{method_name}() 不存在"))
                
    except Exception as e:
        results.append(("SpotModule 方法测试", False, f"❌ 测试失败: {e}"))
    
    return results


def test_prediction_module_methods() -> List[Tuple[str, bool, str]]:
    """测试 PredictionModule 的方法是否存在"""
    results = []
    
    try:
        from quant1024 import Exchange1024ex
        exchange = Exchange1024ex(api_key="test", secret_key="test")
        prediction = exchange.prediction
        
        core_methods = [
            "list_markets",
            "list_active_markets",
            "list_trending_markets",
            "get_market",
            "get_market_stats",
            "get_market_orderbook",
            "mint",
            "redeem",
            "claim",
            "place_order",
            "cancel_order",
            "get_my_positions",
            "get_my_orders",
            "multi_mint",
            "multi_redeem",
        ]
        
        for method_name in core_methods:
            if hasattr(prediction, method_name) and callable(getattr(prediction, method_name)):
                results.append((f"prediction.{method_name}", True, f"✅ prediction.{method_name}() 存在"))
            else:
                results.append((f"prediction.{method_name}", False, f"❌ prediction.{method_name}() 不存在"))
                
    except Exception as e:
        results.append(("PredictionModule 方法测试", False, f"❌ 测试失败: {e}"))
    
    return results


def test_championship_module_methods() -> List[Tuple[str, bool, str]]:
    """测试 ChampionshipModule 的方法是否存在"""
    results = []
    
    try:
        from quant1024 import Exchange1024ex
        exchange = Exchange1024ex(api_key="test", secret_key="test")
        championship = exchange.championship
        
        core_methods = [
            "list_championships",
            "get_championship",
            "get_leaderboard",
            "get_my_rank",
            "get_top3",
        ]
        
        for method_name in core_methods:
            if hasattr(championship, method_name) and callable(getattr(championship, method_name)):
                results.append((f"championship.{method_name}", True, f"✅ championship.{method_name}() 存在"))
            else:
                results.append((f"championship.{method_name}", False, f"❌ championship.{method_name}() 不存在"))
                
    except Exception as e:
        results.append(("ChampionshipModule 方法测试", False, f"❌ 测试失败: {e}"))
    
    return results


def test_account_module_methods() -> List[Tuple[str, bool, str]]:
    """测试 AccountModule 的方法是否存在"""
    results = []
    
    try:
        from quant1024 import Exchange1024ex
        exchange = Exchange1024ex(api_key="test", secret_key="test")
        account = exchange.account
        
        core_methods = [
            "get_overview",
            "get_onchain_status",
            "get_perp_margin",
            "get_perp_trading_stats",
            "get_spot_summary",
            "get_api_keys",
            "get_deposits",
            "get_withdrawals",
            "request_withdrawal",
        ]
        
        for method_name in core_methods:
            if hasattr(account, method_name) and callable(getattr(account, method_name)):
                results.append((f"account.{method_name}", True, f"✅ account.{method_name}() 存在"))
            else:
                results.append((f"account.{method_name}", False, f"❌ account.{method_name}() 不存在"))
                
    except Exception as e:
        results.append(("AccountModule 方法测试", False, f"❌ 测试失败: {e}"))
    
    return results


def test_exceptions_import() -> Tuple[bool, str]:
    """测试异常类导入"""
    try:
        from quant1024 import (
            Quant1024Exception,
            AuthenticationError,
            RateLimitError,
            InvalidParameterError,
            InsufficientMarginError,
            OrderNotFoundError,
            MarketNotFoundError,
            APIError
        )
        return True, "✅ 所有异常类导入成功"
    except ImportError as e:
        return False, f"❌ 异常类导入失败: {e}"


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("quant1024 SDK 模块接口测试")
    print("=" * 60)
    print()
    
    all_passed = True
    total_tests = 0
    passed_tests = 0
    
    # 1. 基础导入测试
    print("📦 1. 基础导入测试")
    print("-" * 40)
    success, msg = test_basic_import()
    print(msg)
    total_tests += 1
    if success:
        passed_tests += 1
    else:
        all_passed = False
        print("\n⚠️  基础导入失败，请先安装 SDK：pip install -e .")
        return
    print()
    
    # 2. 模块导入测试
    print("📦 2. 模块类导入测试")
    print("-" * 40)
    for name, success, msg in test_module_imports():
        print(msg)
        total_tests += 1
        if success:
            passed_tests += 1
        else:
            all_passed = False
    print()
    
    # 3. Exchange1024ex 导入
    print("📦 3. Exchange1024ex 导入测试")
    print("-" * 40)
    success, msg = test_exchange_import()
    print(msg)
    total_tests += 1
    if success:
        passed_tests += 1
    else:
        all_passed = False
    print()
    
    # 4. 接口导入测试
    print("📦 4. 接口类导入测试")
    print("-" * 40)
    for name, success, msg in test_interface_imports():
        print(msg)
        total_tests += 1
        if success:
            passed_tests += 1
        else:
            all_passed = False
    print()
    
    # 5. Exchange 实例化测试
    print("📦 5. Exchange1024ex 实例化测试")
    print("-" * 40)
    success, msg = test_exchange_creation()
    print(msg)
    total_tests += 1
    if success:
        passed_tests += 1
    else:
        all_passed = False
    print()
    
    # 6. 模块访问测试
    print("📦 6. 模块访问测试 (exchange.xxx)")
    print("-" * 40)
    for name, success, msg in test_module_access():
        print(msg)
        total_tests += 1
        if success:
            passed_tests += 1
        else:
            all_passed = False
    print()
    
    # 7. PerpModule 方法测试
    print("📦 7. PerpModule 方法测试")
    print("-" * 40)
    for name, success, msg in test_perp_module_methods():
        print(msg)
        total_tests += 1
        if success:
            passed_tests += 1
        else:
            all_passed = False
    print()
    
    # 8. SpotModule 方法测试
    print("📦 8. SpotModule 方法测试")
    print("-" * 40)
    for name, success, msg in test_spot_module_methods():
        print(msg)
        total_tests += 1
        if success:
            passed_tests += 1
        else:
            all_passed = False
    print()
    
    # 9. PredictionModule 方法测试
    print("📦 9. PredictionModule 方法测试")
    print("-" * 40)
    for name, success, msg in test_prediction_module_methods():
        print(msg)
        total_tests += 1
        if success:
            passed_tests += 1
        else:
            all_passed = False
    print()
    
    # 10. ChampionshipModule 方法测试
    print("📦 10. ChampionshipModule 方法测试")
    print("-" * 40)
    for name, success, msg in test_championship_module_methods():
        print(msg)
        total_tests += 1
        if success:
            passed_tests += 1
        else:
            all_passed = False
    print()
    
    # 11. AccountModule 方法测试
    print("📦 11. AccountModule 方法测试")
    print("-" * 40)
    for name, success, msg in test_account_module_methods():
        print(msg)
        total_tests += 1
        if success:
            passed_tests += 1
        else:
            all_passed = False
    print()
    
    # 12. 异常类导入测试
    print("📦 12. 异常类导入测试")
    print("-" * 40)
    success, msg = test_exceptions_import()
    print(msg)
    total_tests += 1
    if success:
        passed_tests += 1
    else:
        all_passed = False
    print()
    
    # 汇总
    print("=" * 60)
    print(f"测试结果: {passed_tests}/{total_tests} 通过")
    if all_passed:
        print("🎉 所有测试通过！quant1024 SDK 模块接口正常工作")
    else:
        print("⚠️  部分测试失败，请检查上面的错误信息")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
