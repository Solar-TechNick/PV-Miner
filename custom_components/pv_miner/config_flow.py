"""Config flow for PV Miner integration."""
import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_MAX_POWER,
    CONF_MIN_POWER,
    CONF_PRIORITY,
    CONF_SCAN_INTERVAL,
    CONF_SOLAR_SCAN_INTERVAL,
    DEFAULT_MAX_POWER,
    DEFAULT_MIN_POWER,
    DEFAULT_PASSWORD,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SOLAR_SCAN_INTERVAL,
    DEFAULT_USERNAME,
    DOMAIN,
)
from .luxos_api import LuxOSAPI, LuxOSAPIError

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_USERNAME, default=DEFAULT_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD, default=DEFAULT_PASSWORD): cv.string,
})

STEP_POWER_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_MIN_POWER, default=DEFAULT_MIN_POWER): cv.positive_int,
    vol.Required(CONF_MAX_POWER, default=DEFAULT_MAX_POWER): cv.positive_int,
    vol.Required(CONF_PRIORITY, default=1): cv.positive_int,
})

STEP_INTERVALS_DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): cv.positive_int,
    vol.Required(CONF_SOLAR_SCAN_INTERVAL, default=DEFAULT_SOLAR_SCAN_INTERVAL): cv.positive_int,
})


async def validate_input(hass: HomeAssistant, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the user input allows us to connect."""
    api = LuxOSAPI(data[CONF_HOST], data[CONF_USERNAME], data[CONF_PASSWORD])
    
    try:
        if not await api.test_connection():
            raise LuxOSAPIError("Cannot connect to miner")
        
        # Get miner info
        stats = await api.get_stats()
        devs = await api.get_devs()
        
        return {
            "title": data[CONF_NAME],
            "miner_info": {
                "stats": stats,
                "devices": devs
            }
        }
    finally:
        await api.close()


class PVMinerConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PV Miner."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._data = {}

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                self._data.update(user_input)
                return await self.async_step_power()
            except LuxOSAPIError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "example_host": "192.168.1.210",
                "example_name": "Antminer S19j Pro+"
            }
        )

    async def async_step_power(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Configure power settings."""
        errors = {}

        if user_input is not None:
            if user_input[CONF_MIN_POWER] >= user_input[CONF_MAX_POWER]:
                errors["base"] = "invalid_power_range"
            else:
                self._data.update(user_input)
                return await self.async_step_intervals()

        return self.async_show_form(
            step_id="power",
            data_schema=STEP_POWER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "miner_name": self._data.get(CONF_NAME, "Miner")
            }
        )

    async def async_step_intervals(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Configure update intervals."""
        if user_input is not None:
            self._data.update(user_input)
            
            # Check for existing entries
            await self.async_set_unique_id(self._data[CONF_HOST])
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=self._data[CONF_NAME],
                data=self._data
            )

        return self.async_show_form(
            step_id="intervals",
            data_schema=STEP_INTERVALS_DATA_SCHEMA,
            description_placeholders={
                "miner_name": self._data.get(CONF_NAME, "Miner")
            }
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return PVMinerOptionsFlowHandler(config_entry)


class PVMinerOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for PV Miner."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options_schema = vol.Schema({
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=self.config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
            ): cv.positive_int,
            vol.Optional(
                CONF_SOLAR_SCAN_INTERVAL,
                default=self.config_entry.options.get(CONF_SOLAR_SCAN_INTERVAL, DEFAULT_SOLAR_SCAN_INTERVAL)
            ): cv.positive_int,
            vol.Optional(
                CONF_MIN_POWER,
                default=self.config_entry.options.get(CONF_MIN_POWER, DEFAULT_MIN_POWER)
            ): cv.positive_int,
            vol.Optional(
                CONF_MAX_POWER,
                default=self.config_entry.options.get(CONF_MAX_POWER, DEFAULT_MAX_POWER)
            ): cv.positive_int,
            vol.Optional(
                CONF_PRIORITY,
                default=self.config_entry.options.get(CONF_PRIORITY, 1)
            ): cv.positive_int,
        })

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema
        )