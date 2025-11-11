"""
Runtime 监控报告器
"""

import requests
import logging
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import atexit
from datetime import datetime

from .types import RuntimeConfig

logger = logging.getLogger(__name__)


class RuntimeReporter:
    """
    Runtime 监控报告器（简化版）
    
    改进：
    - 移除 exchange 参数（api_base_url 与交易所无关）
    - 使用 RuntimeConfig 直接初始化
    """
    
    def __init__(self, config: RuntimeConfig):
        """
        初始化报告器
        
        Args:
            config: Runtime 配置（包含 api_base_url）
        """
        self.config = config
        
        # HTTP Session
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': config.api_key,
            'Content-Type': 'application/json'
        })
        
        # 异步线程池
        self._executor = ThreadPoolExecutor(
            max_workers=3,
            thread_name_prefix="runtime_reporter"
        )
        
        atexit.register(self._cleanup)
        
        self._runtime_created = False
        self._pending_futures = []
        
        logger.info(
            f"RuntimeReporter initialized: "
            f"runtime_id={config.runtime_id}, "
            f"api_base_url={config.api_base_url}"
        )
    
    def create_runtime(
        self,
        market: str,
        initial_capital: float,
        max_position_size: float
    ) -> bool:
        """
        创建 Runtime
        
        Args:
            market: 交易市场
            initial_capital: 初始资金
            max_position_size: 最大仓位大小
        
        Returns:
            bool: 创建是否成功
        """
        if self._runtime_created:
            logger.warning("Runtime already created")
            return True
        
        try:
            url = f"{self.config.api_base_url}/api/v1/runtimes"
            
            payload = {
                "runtime_id": self.config.runtime_id,
                "strategy_id": self.config.strategy_id,
                "market": market,
                "initial_capital": initial_capital,
                "max_position_size": max_position_size,
                "environment": self.config.environment,
                "sdk_version": self.config.sdk_version,
                "status": "running",
                "start_time": datetime.utcnow().isoformat()
            }
            
            # 添加额外的元数据
            if self.config.extra_metadata:
                payload["metadata"] = self.config.extra_metadata
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code in [200, 201]:
                self._runtime_created = True
                logger.info(f"Runtime created successfully: {self.config.runtime_id}")
                return True
            else:
                logger.error(
                    f"Failed to create runtime: "
                    f"status={response.status_code}, "
                    f"response={response.text}"
                )
                return False
        
        except Exception as e:
            logger.error(f"Error creating runtime: {e}", exc_info=True)
            return False
    
    def update_runtime_status(self, status: str, **kwargs) -> None:
        """
        更新 Runtime 状态（异步）
        
        Args:
            status: 运行状态 (running, stopped, error)
            **kwargs: 其他状态信息
        """
        if not self._runtime_created:
            logger.warning("Runtime not created yet, skipping status update")
            return
        
        future = self._executor.submit(
            self._update_runtime_status_sync,
            status,
            kwargs
        )
        self._pending_futures.append(future)
    
    def _update_runtime_status_sync(self, status: str, extra_data: Dict[str, Any]) -> None:
        """同步更新 Runtime 状态"""
        try:
            url = f"{self.config.api_base_url}/api/v1/runtimes/{self.config.runtime_id}"
            
            payload = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            payload.update(extra_data)
            
            response = self.session.patch(url, json=payload, timeout=10)
            
            if response.status_code != 200:
                logger.warning(
                    f"Failed to update runtime status: "
                    f"status={response.status_code}"
                )
        
        except Exception as e:
            logger.error(f"Error updating runtime status: {e}")
    
    def report_trade(
        self,
        market: str,
        side: str,
        size: float,
        price: float,
        order_id: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        报告交易（异步）
        
        Args:
            market: 交易市场
            side: 交易方向 (buy/sell)
            size: 交易数量
            price: 交易价格
            order_id: 订单ID
            **kwargs: 其他交易信息
        """
        if not self._runtime_created:
            logger.warning("Runtime not created yet, skipping trade report")
            return
        
        future = self._executor.submit(
            self._report_trade_sync,
            market,
            side,
            size,
            price,
            order_id,
            kwargs
        )
        self._pending_futures.append(future)
    
    def _report_trade_sync(
        self,
        market: str,
        side: str,
        size: float,
        price: float,
        order_id: Optional[str],
        extra_data: Dict[str, Any]
    ) -> None:
        """同步报告交易"""
        try:
            url = f"{self.config.api_base_url}/api/v1/trades"
            
            payload = {
                "runtime_id": self.config.runtime_id,
                "strategy_id": self.config.strategy_id,
                "market": market,
                "side": side,
                "size": size,
                "price": price,
                "order_id": order_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            payload.update(extra_data)
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code in [200, 201]:
                logger.debug(f"Trade reported successfully: {side} {size} @ {price}")
            else:
                logger.warning(
                    f"Failed to report trade: "
                    f"status={response.status_code}"
                )
        
        except Exception as e:
            logger.error(f"Error reporting trade: {e}")
    
    def report_signal(
        self,
        market: str,
        signal: int,
        price: float,
        **kwargs
    ) -> None:
        """
        报告交易信号（异步）
        
        Args:
            market: 交易市场
            signal: 交易信号 (1=buy, -1=sell, 0=hold)
            price: 当前价格
            **kwargs: 其他信号信息
        """
        if not self._runtime_created:
            return
        
        future = self._executor.submit(
            self._report_signal_sync,
            market,
            signal,
            price,
            kwargs
        )
        self._pending_futures.append(future)
    
    def _report_signal_sync(
        self,
        market: str,
        signal: int,
        price: float,
        extra_data: Dict[str, Any]
    ) -> None:
        """同步报告信号"""
        try:
            url = f"{self.config.api_base_url}/api/v1/signals"
            
            payload = {
                "runtime_id": self.config.runtime_id,
                "strategy_id": self.config.strategy_id,
                "market": market,
                "signal": signal,
                "price": price,
                "timestamp": datetime.utcnow().isoformat()
            }
            payload.update(extra_data)
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code not in [200, 201]:
                logger.warning(
                    f"Failed to report signal: "
                    f"status={response.status_code}"
                )
        
        except Exception as e:
            logger.error(f"Error reporting signal: {e}")
    
    def report_position(
        self,
        market: str,
        position_size: float,
        entry_price: float,
        current_price: float,
        **kwargs
    ) -> None:
        """
        报告持仓信息（异步）
        
        Args:
            market: 交易市场
            position_size: 持仓大小
            entry_price: 入场价格
            current_price: 当前价格
            **kwargs: 其他持仓信息
        """
        if not self._runtime_created:
            return
        
        future = self._executor.submit(
            self._report_position_sync,
            market,
            position_size,
            entry_price,
            current_price,
            kwargs
        )
        self._pending_futures.append(future)
    
    def _report_position_sync(
        self,
        market: str,
        position_size: float,
        entry_price: float,
        current_price: float,
        extra_data: Dict[str, Any]
    ) -> None:
        """同步报告持仓"""
        try:
            url = f"{self.config.api_base_url}/api/v1/positions"
            
            # 计算 PnL
            pnl = 0.0
            pnl_pct = 0.0
            if position_size != 0 and entry_price > 0:
                pnl = (current_price - entry_price) * position_size
                pnl_pct = (current_price - entry_price) / entry_price
            
            payload = {
                "runtime_id": self.config.runtime_id,
                "strategy_id": self.config.strategy_id,
                "market": market,
                "position_size": position_size,
                "entry_price": entry_price,
                "current_price": current_price,
                "pnl": pnl,
                "pnl_pct": pnl_pct,
                "timestamp": datetime.utcnow().isoformat()
            }
            payload.update(extra_data)
            
            response = self.session.post(url, json=payload, timeout=10)
            
            if response.status_code not in [200, 201]:
                logger.warning(
                    f"Failed to report position: "
                    f"status={response.status_code}"
                )
        
        except Exception as e:
            logger.error(f"Error reporting position: {e}")
    
    def _cleanup(self):
        """清理资源"""
        try:
            # 等待所有挂起的任务完成
            for future in self._pending_futures:
                try:
                    future.result(timeout=5)
                except Exception as e:
                    logger.error(f"Error waiting for pending task: {e}")
            
            self._executor.shutdown(wait=False)
            self.session.close()
            
            logger.info("RuntimeReporter cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

