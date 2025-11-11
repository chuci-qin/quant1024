"""
Runtime 监控报告器
"""

import requests
import logging
import time
from typing import Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import atexit
from datetime import datetime

from .types import RuntimeConfig

logger = logging.getLogger(__name__)


# ============================================================================
# Retry Mechanism
# ============================================================================

def retry_with_backoff(max_retries=3, base_delay=1.0):
    """
    简单的重试装饰器，使用指数退避
    
    Args:
        max_retries: 最大重试次数
        base_delay: 基础延迟（秒）
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (requests.RequestException, requests.Timeout) as e:
                    if attempt == max_retries:
                        # 最后一次尝试失败，抛出异常
                        logger.error(f"Failed after {max_retries} retries: {e}")
                        raise
                    
                    # 计算延迟时间（指数退避）
                    delay = base_delay * (2 ** attempt)
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}/{max_retries + 1}), "
                        f"retrying in {delay}s: {e}"
                    )
                    time.sleep(delay)
                except Exception as e:
                    # 非网络错误，直接抛出
                    logger.error(f"Non-retryable error: {e}")
                    raise
        return wrapper
    return decorator


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
        
        # 统计计数器
        self._stats = {
            'signals_sent': 0,
            'signals_failed': 0,
            'trades_sent': 0,
            'trades_failed': 0,
            'positions_sent': 0,
            'positions_failed': 0,
        }
        
        logger.info(
            f"RuntimeReporter initialized: "
            f"runtime_id={config.runtime_id}, "
            f"api_base_url={config.api_base_url}"
        )
    
    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def _post_with_retry(self, url: str, payload: Dict[str, Any]) -> requests.Response:
        """
        带重试的POST请求
        
        使用指数退避策略，最多重试3次。
        
        Args:
            url: 请求URL
            payload: 请求体
            
        Returns:
            Response对象
            
        Raises:
            requests.RequestException: 重试失败后抛出
        """
        response = self.session.post(url, json=payload, timeout=10)
        response.raise_for_status()  # 非2xx状态码会抛出异常
        return response
    
    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def _patch_with_retry(self, url: str, payload: Dict[str, Any]) -> requests.Response:
        """带重试的PATCH请求"""
        response = self.session.patch(url, json=payload, timeout=10)
        response.raise_for_status()
        return response
    
    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return self._stats.copy()
    
    def _cleanup_completed_futures(self):
        """清理已完成的futures"""
        self._pending_futures = [f for f in self._pending_futures if not f.done()]
    
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
            
            # 使用重试机制
            response = self._post_with_retry(url, payload)
            
            self._runtime_created = True
            logger.info(f"✅ Runtime created successfully: {self.config.runtime_id}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Error creating runtime (after retries): {e}", exc_info=True)
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
            # ✨ RESTful: runtime_id 在 URL 中
            url = f"{self.config.api_base_url}/api/v1/runtimes/{self.config.runtime_id}"
            
            payload = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            payload.update(extra_data)
            
            # 使用重试机制
            response = self._patch_with_retry(url, payload)
            logger.debug(f"✅ Runtime status updated: {status}")
        
        except Exception as e:
            logger.error(f"❌ Error updating runtime status (after retries): {e}")
    
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
            # ✨ RESTful: runtime_id 在 URL 中
            url = f"{self.config.api_base_url}/api/v1/runtimes/{self.config.runtime_id}/trades"
            
            payload = {
                "market": market,
                "side": side,
                "size": size,
                "price": price,
                "order_id": order_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            payload.update(extra_data)
            
            # 使用重试机制
            response = self._post_with_retry(url, payload)
            
            self._stats['trades_sent'] += 1
            logger.debug(f"✅ Trade reported: {side} {size} @ {price}")
        
        except Exception as e:
            self._stats['trades_failed'] += 1
            logger.error(f"❌ Error reporting trade (after retries): {e}")
        finally:
            # 定期清理已完成的futures
            if len(self._pending_futures) > 100:
                self._cleanup_completed_futures()
    
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
            # ✨ RESTful: runtime_id 在 URL 中
            url = f"{self.config.api_base_url}/api/v1/runtimes/{self.config.runtime_id}/signals"
            
            payload = {
                "market": market,
                "signal": signal,
                "price": price,
                "timestamp": datetime.utcnow().isoformat()
            }
            payload.update(extra_data)
            
            # 使用重试机制
            response = self._post_with_retry(url, payload)
            
            self._stats['signals_sent'] += 1
            logger.debug(f"✅ Signal reported: {signal} @ {price}")
        
        except Exception as e:
            self._stats['signals_failed'] += 1
            logger.error(f"❌ Error reporting signal (after retries): {e}")
        finally:
            if len(self._pending_futures) > 100:
                self._cleanup_completed_futures()
    
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
            # ✨ RESTful: runtime_id 在 URL 中
            url = f"{self.config.api_base_url}/api/v1/runtimes/{self.config.runtime_id}/positions"
            
            # 计算 PnL（支持做空：position_size可以为负）
            pnl = 0.0
            pnl_pct = 0.0
            if position_size != 0 and entry_price > 0:
                pnl = (current_price - entry_price) * position_size
                pnl_pct = (current_price - entry_price) / entry_price
            
            payload = {
                "market": market,
                "position_size": position_size,
                "entry_price": entry_price,
                "current_price": current_price,
                "pnl": pnl,
                "pnl_pct": pnl_pct,
                "timestamp": datetime.utcnow().isoformat()
            }
            payload.update(extra_data)
            
            # 使用重试机制
            response = self._post_with_retry(url, payload)
            
            self._stats['positions_sent'] += 1
            logger.debug(f"✅ Position reported: {position_size} @ {current_price}, PnL: {pnl}")
        
        except Exception as e:
            self._stats['positions_failed'] += 1
            logger.error(f"❌ Error reporting position (after retries): {e}")
        finally:
            if len(self._pending_futures) > 100:
                self._cleanup_completed_futures()
    
    def _cleanup(self):
        """清理资源"""
        try:
            # 使用concurrent.futures.wait批量等待（最多5秒）
            from concurrent.futures import wait, ALL_COMPLETED
            
            if self._pending_futures:
                logger.info(f"Waiting for {len(self._pending_futures)} pending tasks...")
                done, pending = wait(self._pending_futures, timeout=5, return_when=ALL_COMPLETED)
                
                if pending:
                    logger.warning(f"{len(pending)} tasks did not complete in time, cancelling...")
                    for future in pending:
                        future.cancel()
                
                # 记录失败的任务
                for future in done:
                    try:
                        future.result()
                    except Exception as e:
                        logger.error(f"Task failed: {e}")
            
            self._executor.shutdown(wait=False)
            self.session.close()
            
            # 输出统计信息
            logger.info(
                f"RuntimeReporter cleanup completed. Stats: "
                f"signals={self._stats['signals_sent']}/{self._stats['signals_sent'] + self._stats['signals_failed']}, "
                f"trades={self._stats['trades_sent']}/{self._stats['trades_sent'] + self._stats['trades_failed']}, "
                f"positions={self._stats['positions_sent']}/{self._stats['positions_sent'] + self._stats['positions_failed']}"
            )
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

