"""
Test 1024ex Exchange connector

Contains test cases for the Exchange1024ex connector.
Tests import functionality and basic API structure.
"""

import pytest
import responses
from quant1024.exchanges.exchange_1024ex import Exchange1024ex
from quant1024.exceptions import (
    AuthenticationError,
    RateLimitError,
    MarketNotFoundError,
    APIError
)


# ========== Fixtures ==========

@pytest.fixture
def client():
    """Create test client"""
    return Exchange1024ex(
        api_key="test_api_key",
        secret_key="test_secret_key",
        base_url="https://api.1024ex.com"
    )


# ========== Import and Initialization Tests ==========

def test_exchange_import():
    """Test Exchange1024ex can be imported"""
    assert Exchange1024ex is not None


def test_exchange_init():
    """Test Exchange1024ex initialization"""
    client = Exchange1024ex(
        api_key="test_key",
        secret_key="test_secret"
    )
    assert client.api_key == "test_key"
    assert client.secret_key == "test_secret"
    assert client.base_url == "https://api.1024ex.com"


def test_exchange_init_custom_url():
    """Test Exchange1024ex with custom URL"""
    client = Exchange1024ex(
        api_key="test",
        base_url="http://localhost:8090"
    )
    assert client.base_url == "http://localhost:8090"


def test_exchange_modules_exist(client):
    """Test all modules are accessible"""
    assert hasattr(client, 'perp')
    assert hasattr(client, 'spot')
    assert hasattr(client, 'prediction')
    assert hasattr(client, 'championship')
    assert hasattr(client, 'account')


def test_perp_module_methods(client):
    """Test perp module has expected methods"""
    perp = client.perp
    assert hasattr(perp, 'get_markets')
    assert hasattr(perp, 'get_ticker')
    assert hasattr(perp, 'get_orderbook')
    assert hasattr(perp, 'place_order')
    assert hasattr(perp, 'cancel_order')


def test_account_module_methods(client):
    """Test account module has expected methods"""
    account = client.account
    assert hasattr(account, 'get_overview')
    assert hasattr(account, 'get_perp_margin')


# ========== System Endpoint Tests ==========

@responses.activate
def test_get_server_time(client):
    """Test get server time"""
    responses.add(
        responses.GET,
        "https://api.1024ex.com/api/v1/time",
        json={
            "success": True,
            "data": {
                "server_time": 1762911479265,
                "timezone": "UTC"
            },
            "timestamp": 1762911479265
        },
        status=200
    )
    
    result = client.get_server_time()
    assert result["success"] == True
    assert "data" in result


@responses.activate
def test_get_health(client):
    """Test health check"""
    responses.add(
        responses.GET,
        "https://api.1024ex.com/api/v1/health",
        json={"status": "ok", "services": {"database": "ok"}},
        status=200
    )
    
    result = client.get_health()
    assert result["status"] == "ok"


@responses.activate
def test_get_exchange_info(client):
    """Test get exchange info"""
    responses.add(
        responses.GET,
        "https://api.1024ex.com/api/v1/exchange-info",
        json={"name": "1024ex", "version": "4.1.0"},
        status=200
    )
    
    result = client.get_exchange_info()
    assert "name" in result


# ========== Market Data Tests (using correct perp paths) ==========

@responses.activate
def test_get_markets(client):
    """Test get markets"""
    responses.add(
        responses.GET,
        "https://api.1024ex.com/api/v1/perp/markets",
        json={
            "data": [
                {"market": "BTC-USDC", "base_asset": "BTC"},
                {"market": "ETH-USDC", "base_asset": "ETH"}
            ]
        },
        status=200
    )
    
    result = client.get_markets()
    assert len(result) == 2
    assert result[0]["market"] == "BTC-USDC"


@responses.activate
def test_get_ticker(client):
    """Test get ticker"""
    responses.add(
        responses.GET,
        "https://api.1024ex.com/api/v1/perp/ticker/BTC-USDC",
        json={
            "market": "BTC-USDC",
            "last_price": "60000.00",
            "mark_price": "60001.00"
        },
        status=200
    )
    
    result = client.get_ticker("BTC-USDC")
    assert result["market"] == "BTC-USDC"
    assert "last_price" in result


# ========== Error Handling Tests ==========

@responses.activate
def test_authentication_error(client):
    """Test authentication error"""
    responses.add(
        responses.GET,
        "https://api.1024ex.com/api/v1/account/overview",
        status=401
    )
    
    with pytest.raises(AuthenticationError):
        client.account.get_overview()


@responses.activate
def test_rate_limit_error(client):
    """Test rate limit error"""
    responses.add(
        responses.GET,
        "https://api.1024ex.com/api/v1/perp/markets",
        status=429,
        headers={'Retry-After': '60'}
    )
    
    with pytest.raises(RateLimitError):
        client.get_markets()


@responses.activate
def test_api_error(client):
    """Test API error"""
    responses.add(
        responses.POST,
        "https://api.1024ex.com/api/v1/perp/orders",
        json={"message": "Insufficient margin"},
        status=400
    )
    
    with pytest.raises(APIError):
        client.perp.place_order(
            market="BTC-USDC",
            side="long",
            order_type="limit",
            price="60000",
            size="100"
        )


# ========== Public API Import Tests ==========

def test_public_api_import_exchange():
    """Test Exchange1024ex can be imported from public API"""
    from quant1024 import Exchange1024ex
    assert Exchange1024ex is not None


def test_public_api_import_qc():
    """Test qc module can be imported from public API"""
    from quant1024 import qc
    assert qc is not None
    assert hasattr(qc, 'QCCredentials')
    assert hasattr(qc, 'QuantConnectAPI')


def test_blocked_import_raises():
    """Test that blocked imports raise ImportError"""
    with pytest.raises(ImportError):
        from quant1024 import QuantStrategy
    
    with pytest.raises(ImportError):
        from quant1024 import DataRetriever
