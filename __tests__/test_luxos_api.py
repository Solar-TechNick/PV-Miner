"""Tests for LuxOS API client."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp

from custom_components.pv_miner.luxos_api import LuxOSAPI, LuxOSAPIError


@pytest.fixture
def api():
    """Create a LuxOS API instance for testing."""
    return LuxOSAPI("192.168.1.210", "root", "rootz")


@pytest.mark.asyncio
async def test_login_success(api):
    """Test successful login."""
    mock_response = {
        "session_id": "test_session_123"
    }
    
    with patch.object(api, '_make_request', return_value=mock_response):
        result = await api.login()
        assert result is True
        assert api.session_id == "test_session_123"


@pytest.mark.asyncio
async def test_login_failure(api):
    """Test login failure."""
    mock_response = {
        "error": "Invalid credentials"
    }
    
    with patch.object(api, '_make_request', return_value=mock_response):
        result = await api.login()
        assert result is False
        assert api.session_id is None


@pytest.mark.asyncio
async def test_get_stats(api):
    """Test getting miner statistics."""
    mock_stats = {
        "STATS": [
            {},
            {"GHS 5s": 100000, "Power": 3200}
        ]
    }
    
    with patch.object(api, '_make_request', return_value=mock_stats):
        stats = await api.get_stats()
        assert stats == mock_stats


@pytest.mark.asyncio
async def test_set_frequency(api):
    """Test setting frequency."""
    mock_response = {"STATUS": "OK"}
    
    with patch.object(api, '_make_request', return_value=mock_response):
        result = await api.set_frequency(2)
        assert result == mock_response


@pytest.mark.asyncio
async def test_connection_error(api):
    """Test connection error handling."""
    with patch.object(api, '_get_session') as mock_session:
        mock_session.return_value.post.side_effect = aiohttp.ClientError("Connection failed")
        
        with pytest.raises(LuxOSAPIError):
            await api._make_request("test")


@pytest.mark.asyncio
async def test_test_connection_success(api):
    """Test successful connection test."""
    with patch.object(api, 'login', return_value=True), \
         patch.object(api, 'get_stats', return_value={}):
        result = await api.test_connection()
        assert result is True


@pytest.mark.asyncio
async def test_test_connection_failure(api):
    """Test failed connection test."""
    with patch.object(api, 'login', side_effect=LuxOSAPIError("Connection failed")):
        result = await api.test_connection()
        assert result is False


@pytest.mark.asyncio
async def test_close_session(api):
    """Test closing API session."""
    mock_session = AsyncMock()
    api._session = mock_session
    
    await api.close()
    mock_session.close.assert_called_once()