"""Tests for PV Miner config flow."""
import pytest
from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.pv_miner.config_flow import PVMinerConfigFlow
from custom_components.pv_miner.const import DOMAIN


@pytest.fixture
def hass():
    """Create a HomeAssistant instance for testing."""
    return AsyncMock(spec=HomeAssistant)


@pytest.mark.asyncio
async def test_form(hass):
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}


@pytest.mark.asyncio
async def test_form_invalid_host(hass):
    """Test we handle invalid host."""
    with patch(
        "custom_components.pv_miner.config_flow.validate_input",
        side_effect=Exception,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
            data={
                CONF_HOST: "invalid_host",
                CONF_NAME: "Test Miner",
                CONF_USERNAME: "root",
                CONF_PASSWORD: "rootz",
            },
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "unknown"}


@pytest.mark.asyncio
async def test_form_cannot_connect(hass):
    """Test we handle cannot connect error."""
    from custom_components.pv_miner.luxos_api import LuxOSAPIError
    
    with patch(
        "custom_components.pv_miner.config_flow.validate_input",
        side_effect=LuxOSAPIError,
    ):
        result = await hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_USER},
            data={
                CONF_HOST: "192.168.1.210",
                CONF_NAME: "Test Miner",
                CONF_USERNAME: "root",
                CONF_PASSWORD: "rootz",
            },
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}