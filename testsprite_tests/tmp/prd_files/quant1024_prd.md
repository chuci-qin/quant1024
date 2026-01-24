# quant1024 - Product Requirements Document

## Product Overview
quant1024 is a multi-source quantitative trading toolkit for structured data retrieval and real-time trading. It supports exchanges, financial data providers, and blockchain sources with a unified interface.

## Core Features

### 1. QuantStrategy Abstract Base Class
- Abstract base class for creating custom trading strategies
- Methods: `generate_signals()`, `calculate_position()`, `backtest()`
- Supports strategy initialization with custom parameters
- Automatic initialization on first backtest

### 2. Utility Functions
- `calculate_returns(prices)`: Calculate returns from price series
- `calculate_sharpe_ratio(returns)`: Calculate Sharpe ratio for performance evaluation
- Handle edge cases: empty data, zero prices, single values

### 3. Multi-Exchange Support
- Unified interface via `BaseExchange` abstract class
- `Exchange1024ex` implementation for 1024 Exchange
- Modular architecture with separate modules:
  - PerpModule: Perpetual futures trading
  - SpotModule: Spot trading
  - PredictionModule: Prediction markets
  - ChampionshipModule: Trading championships
  - AccountModule: Account management

### 4. Unified Interfaces
- `IMarketData`: Market data retrieval interface
- `ITrading`: Trading operations interface
- `IPositions`: Position management interface
- `IAdvancedOrders`: Advanced order types interface

### 5. Data Retrieval System
- `DataRetriever`: Multi-source data aggregation
- `BacktestDataset`: Optimized dataset for backtesting
- Adapters for different data sources:
  - Exchange adapter
  - Finance adapter (Yahoo Finance)
  - Blockchain adapter (Web3)

### 6. Live Trading
- `LiveTrader`: Real-time trading execution
- `start_trading()`: Entry point for live trading
- WebSocket support for real-time data
- Webhook callbacks for order events

### 7. Monitor Feeds
- `RuntimeReporter`: Trading activity monitoring
- `RuntimeConfig`: Runtime configuration management

### 8. Exception Handling
- Custom exceptions for different error scenarios:
  - `AuthenticationError`: API authentication failures
  - `RateLimitError`: Rate limit exceeded
  - `InvalidParameterError`: Invalid parameters
  - `InsufficientMarginError`: Margin requirements not met
  - `OrderNotFoundError`: Order not found
  - `MarketNotFoundError`: Market not found
  - `APIError`: Generic API errors

## Technical Requirements
- Python >= 3.8
- Dependencies: requests, pydantic, pandas, numpy
- Optional: yfinance (Yahoo Finance), web3 (blockchain)
- Test framework: pytest

## User Stories

### US1: Create Custom Strategy
As a quantitative trader, I want to create a custom trading strategy by inheriting from QuantStrategy, so that I can implement my own signal generation and position calculation logic.

### US2: Backtest Strategy
As a trader, I want to backtest my strategy with historical price data, so that I can evaluate its performance before live trading.

### US3: Calculate Performance Metrics
As a trader, I want to calculate returns and Sharpe ratio, so that I can measure strategy performance.

### US4: Connect to Exchange
As a trader, I want to connect to 1024 Exchange using the unified interface, so that I can execute trades programmatically.

### US5: Retrieve Market Data
As a trader, I want to retrieve market data from multiple sources, so that I can analyze market conditions.

### US6: Live Trading
As a trader, I want to execute live trades with real-time data, so that I can profit from my strategies.

### US7: Monitor Trading Activity
As a trader, I want to monitor my trading activity in real-time, so that I can track performance and detect issues.

## Acceptance Criteria

### AC1: Strategy Inheritance
- Can inherit from QuantStrategy
- Must implement generate_signals() and calculate_position()
- Can run backtest() and get results

### AC2: Utility Functions
- calculate_returns() handles empty, single, and multiple prices
- calculate_sharpe_ratio() handles edge cases correctly
- Returns are accurate within floating-point precision

### AC3: Exchange Connection
- Can create Exchange1024ex instance
- Can access modular APIs (perp, spot, etc.)
- Authentication is handled automatically

### AC4: Data Retrieval
- Can retrieve data from multiple sources
- Data is returned in standardized format
- Handles errors gracefully

### AC5: Live Trading
- Can start live trading session
- Receives real-time data updates
- Can execute trades

### AC6: Error Handling
- All custom exceptions inherit from Quant1024Exception
- Error messages are informative
- Errors don't crash the application

