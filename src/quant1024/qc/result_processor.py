"""
Backtest Result Processor
"""

import json
from typing import Dict, Any


class BacktestResultProcessor:
    """Backtest result processing and export"""
    
    @staticmethod
    def get_summary(backtest: Dict) -> Dict[str, Any]:
        """Extract backtest summary"""
        statistics = backtest.get("statistics", {})
        
        return {
            "Total Return": statistics.get("Net Profit", "N/A"),
            "Annual Return": statistics.get("Compounding Annual Return", "N/A"),
            "Sharpe Ratio": statistics.get("Sharpe Ratio", "N/A"),
            "Max Drawdown": statistics.get("Drawdown", "N/A"),
            "Alpha": statistics.get("Alpha", "N/A"),
            "Beta": statistics.get("Beta", "N/A"),
            "Total Orders": statistics.get("Total Orders", "N/A"),
            "Win Rate": statistics.get("Win Rate", "N/A"),
        }
    
    @staticmethod
    def get_full_data(backtest: Dict) -> Dict[str, Any]:
        """Get complete backtest data for custom dashboard"""
        statistics = backtest.get("statistics", {})
        
        return {
            # Top key metrics
            "summary": {
                "equity": statistics.get("Equity", "N/A"),
                "fees": statistics.get("Fees", "N/A"),
                "holdings": statistics.get("Holdings", "N/A"),
                "net_profit": statistics.get("Net Profit", "N/A"),
                "psr": statistics.get("Probabilistic Sharpe Ratio", "N/A"),
                "return": statistics.get("Total Return", "N/A"),
                "unrealized": statistics.get("Unrealized", "N/A"),
                "volume": statistics.get("Total Volume", "N/A"),
            },
            
            # Complete statistics
            "statistics": statistics,
            
            # Equity curve data
            "charts": backtest.get("charts", {}),
            
            # Trade records
            "trades": backtest.get("trades", []),
            
            # Order records
            "orders": backtest.get("orders", {}),
            
            # Holdings info
            "holdings": backtest.get("holdings", {}),
            
            # Risk metrics
            "risk_metrics": {
                "alpha": statistics.get("Alpha", "N/A"),
                "beta": statistics.get("Beta", "N/A"),
                "sharpe_ratio": statistics.get("Sharpe Ratio", "N/A"),
                "sortino_ratio": statistics.get("Sortino Ratio", "N/A"),
                "treynor_ratio": statistics.get("Treynor Ratio", "N/A"),
                "max_drawdown": statistics.get("Drawdown", "N/A"),
                "var": statistics.get("Value at Risk", "N/A"),
            },
            
            # Backtest metadata
            "meta": {
                "backtest_id": backtest.get("backtestId"),
                "project_id": backtest.get("projectId"),
                "name": backtest.get("name"),
                "created": backtest.get("created"),
                "completed": backtest.get("completed"),
            },
            
            # Raw complete data
            "raw": backtest,
        }
    
    @staticmethod
    def export_chart_data(backtest: Dict) -> Dict[str, Any]:
        """Export chart data for frontend bindings"""
        charts = backtest.get("charts", {})
        result = {}
        
        # Strategy Equity chart
        if "Strategy Equity" in charts:
            equity_chart = charts["Strategy Equity"]
            series = equity_chart.get("Series", {})
            
            if "Equity" in series:
                equity_data = series["Equity"].get("Values", [])
                result["equity_curve"] = [
                    {"time": point.get("x"), "value": point.get("y")}
                    for point in equity_data
                ]
            
            if "Return" in series:
                return_data = series["Return"].get("Values", [])
                result["return_curve"] = [
                    {"time": point.get("x"), "value": point.get("y")}
                    for point in return_data
                ]
        
        # Drawdown chart
        if "Drawdown" in charts:
            dd_chart = charts["Drawdown"]
            series = dd_chart.get("Series", {})
            if "Equity Drawdown" in series:
                dd_data = series["Equity Drawdown"].get("Values", [])
                result["drawdown_curve"] = [
                    {"time": point.get("x"), "value": point.get("y")}
                    for point in dd_data
                ]
        
        # Benchmark comparison
        if "Benchmark" in charts:
            bm_chart = charts["Benchmark"]
            series = bm_chart.get("Series", {})
            if "Benchmark" in series:
                bm_data = series["Benchmark"].get("Values", [])
                result["benchmark_curve"] = [
                    {"time": point.get("x"), "value": point.get("y")}
                    for point in bm_data
                ]
        
        return result
    
    @staticmethod
    def parse_equity_curve(charts_data: Dict) -> list:
        """Parse equity curve data"""
        equity_curve = []
        if "Strategy Equity" in charts_data:
            series = charts_data["Strategy Equity"].get("Series", {})
            if "Equity" in series:
                for point in series["Equity"].get("Values", []):
                    equity_curve.append({
                        "timestamp": point.get("x"),
                        "equity": point.get("y")
                    })
        return equity_curve
    
    @staticmethod
    def parse_drawdown_curve(charts_data: Dict) -> list:
        """Parse drawdown data"""
        drawdown_curve = []
        if "Drawdown" in charts_data:
            series = charts_data["Drawdown"].get("Series", {})
            if "Equity Drawdown" in series:
                for point in series["Equity Drawdown"].get("Values", []):
                    drawdown_curve.append({
                        "timestamp": point.get("x"),
                        "drawdown": point.get("y")
                    })
        return drawdown_curve
    
    @classmethod
    def export_to_json(
        cls,
        project_id: int,
        backtest_id: str,
        backtest: Dict,
        charts_data: Dict,
        orders_data: list,
        output_file: str
    ) -> str:
        """Export complete data to JSON file"""
        full_data = cls.get_full_data(backtest)
        equity_curve = cls.parse_equity_curve(charts_data)
        drawdown_curve = cls.parse_drawdown_curve(charts_data)
        
        export_data = {
            "project_id": project_id,
            "backtest_id": backtest_id,
            "url": f"https://www.quantconnect.com/project/{project_id}",
            
            # Top summary metrics
            "summary": {
                "start_equity": full_data["statistics"].get("Start Equity", "1000000"),
                "end_equity": full_data["statistics"].get("End Equity", "N/A"),
                "net_profit": full_data["statistics"].get("Net Profit", "N/A"),
                "total_fees": full_data["statistics"].get("Total Fees", "N/A"),
                "total_return": full_data["statistics"].get("Net Profit", "N/A"),
                "psr": full_data["statistics"].get("Probabilistic Sharpe Ratio", "N/A"),
            },
            
            # Complete statistics
            "statistics": full_data["statistics"],
            
            # Risk metrics
            "risk_metrics": full_data["risk_metrics"],
            
            # Chart data
            "charts": {
                "equity_curve": equity_curve,
                "drawdown_curve": drawdown_curve,
                "raw_charts": list(charts_data.keys()),
            },
            
            # Order records
            "orders": orders_data,
            
            # Raw chart data
            "raw_charts_data": charts_data,
        }
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
        
        return output_file
