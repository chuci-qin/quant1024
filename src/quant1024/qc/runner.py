"""
Backtest Runner
"""

import os
import time
from datetime import datetime, timezone
from typing import Dict, Optional

from .models import QCCredentials
from .client import QuantConnectAPI
from .result_processor import BacktestResultProcessor


# Backtest result save directory
BACKTEST_RESULT_DIR = "backtest_result"


def get_strategy_source_code(strategy_file: str) -> str:
    """
    Read source code from strategy file
    
    Args:
        strategy_file: Path to strategy file
        
    Returns:
        Strategy code that can run on QuantConnect
    """
    with open(strategy_file, 'r', encoding='utf-8') as f:
        return f.read()


def run_backtest(
    user_id: str,
    api_token: str,
    strategy_file: str,
    project_name: Optional[str] = None,
    export_json: bool = False
) -> Dict:
    """
    Run complete backtest workflow
    
    Args:
        user_id: QuantConnect User ID
        api_token: QuantConnect API Token
        strategy_file: Path to strategy file
        project_name: Project name (optional)
        export_json: Whether to export JSON data
        
    Returns:
        Backtest result
    """
    
    print("\n" + "=" * 60)
    print("   🎯 QuantConnect REST API Backtest")
    print("=" * 60)
    
    # Read strategy code
    algorithm_code = get_strategy_source_code(strategy_file)
    print(f"📖 Strategy loaded: {strategy_file}")
    
    # Create API client
    credentials = QCCredentials(user_id=user_id, api_token=api_token)
    api = QuantConnectAPI(credentials)
    
    try:
        # 1. Authenticate
        api.authenticate()
        
        # 2. Create project
        if project_name is None:
            # Generate project name from filename
            base_name = os.path.basename(strategy_file).replace('.py', '')
            project_name = f"{base_name}_{int(time.time())}"
        
        project_id = api.create_project(project_name)
        
        # 3. Upload code
        api.create_file(project_id, "main.py", algorithm_code)
        
        # 4. Compile
        compile_id = api.compile(project_id)
        api.wait_for_compile(project_id, compile_id)
        
        # 5. Run backtest
        backtest_name = f"backtest_{int(time.time())}"
        backtest_id = api.create_backtest(project_id, compile_id, backtest_name)
        backtest = api.wait_for_backtest(project_id, backtest_id)
        
        # 6. Output results
        results = BacktestResultProcessor.get_summary(backtest)
        
        print("\n" + "=" * 60)
        print("   📊 Backtest Results")
        print("=" * 60)
        
        for key, value in results.items():
            print(f"   {key:15s}: {value}")
        
        print("=" * 60)
        print("\n✅ Backtest complete!")
        print(f"   Project ID: {project_id}")
        print(f"   Backtest ID: {backtest_id}")
        print(f"   View details: https://www.quantconnect.com/project/{project_id}")
        
        # 7. Export complete data to JSON
        if export_json:
            # Get additional chart and order data
            try:
                backtest_with_charts = api.get_full_backtest_with_charts(project_id, backtest_id)
                charts_data = backtest_with_charts.get("charts", {})
            except Exception as e:
                print(f"   ⚠️ Unable to get chart data: {e}")
                charts_data = {}
            
            try:
                orders_data = api.get_backtest_orders(project_id, backtest_id)
            except Exception as e:
                print(f"   ⚠️ Unable to get order data: {e}")
                orders_data = []
            
            # Create result directory
            os.makedirs(BACKTEST_RESULT_DIR, exist_ok=True)
            
            # Generate filename using UTC time (format: YYYY-MM-DD_HH-MM-SS)
            utc_now = datetime.now(timezone.utc)
            timestamp_str = utc_now.strftime("%Y-%m-%d_%H-%M-%S")
            output_file = os.path.join(BACKTEST_RESULT_DIR, f"{timestamp_str}.json")
            
            BacktestResultProcessor.export_to_json(
                project_id=project_id,
                backtest_id=backtest_id,
                backtest=backtest,
                charts_data=charts_data,
                orders_data=orders_data,
                output_file=output_file
            )
            
            equity_curve = BacktestResultProcessor.parse_equity_curve(charts_data)
            print(f"\n📁 Complete data exported: {output_file}")
            print(f"   Equity curve data points: {len(equity_curve)}")
            print(f"   Order records: {len(orders_data)}")
            print("   Can be used to build custom dashboard!")
        
        return backtest
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
