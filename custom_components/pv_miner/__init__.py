"""The PV Miner integration."""
import asyncio
import logging
from datetime import timedelta
from typing import Any, Dict

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
)
from .luxos_api import LuxOSAPI, LuxOSAPIError

_LOGGER = logging.getLogger(__name__)

PLATFORMS = [Platform.SENSOR, Platform.SWITCH, Platform.NUMBER, Platform.SELECT]


class PVMinerCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the miner."""

    def __init__(self, hass: HomeAssistant, api: LuxOSAPI, scan_interval: int) -> None:
        """Initialize the coordinator."""
        self.api = api
        update_interval = timedelta(seconds=scan_interval)
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from the miner."""
        try:
            # Get all miner data
            stats = await self.api.get_stats()
            devs = await self.api.get_devs()
            pools = await self.api.get_pools()
            
            # Get additional sensor data
            power = await self.api._execute_command("power", "")
            temps = await self.api._execute_command("temps", "")
            fans = await self.api._execute_command("fans", "")
            
            return {
                "stats": stats,
                "devs": devs,
                "pools": pools,
                "power": power,
                "temps": temps,
                "fans": fans,
                "connected": True
            }
        except LuxOSAPIError as err:
            _LOGGER.error("Error communicating with miner: %s", err)
            raise UpdateFailed(f"Error communicating with miner: {err}")


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PV Miner from a config entry."""
    host = entry.data[CONF_HOST]
    username = entry.data[CONF_USERNAME]
    password = entry.data[CONF_PASSWORD]
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL))

    api = LuxOSAPI(host, username, password)
    
    # Test connection
    try:
        if not await api.test_connection():
            _LOGGER.error("Cannot connect to miner at %s", host)
            return False
    except LuxOSAPIError as err:
        _LOGGER.error("Error connecting to miner: %s", err)
        return False

    # Create coordinator
    coordinator = PVMinerCoordinator(hass, api, scan_interval)
    
    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator and API
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "api": api,
        "config": entry.data,
    }

    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Setup services
    await _async_setup_services(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        # Close API connection
        api = hass.data[DOMAIN][entry.entry_id]["api"]
        await api.close()
        
        # Remove entry from data
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def _async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for the integration."""
    from .services import async_setup_services
    await async_setup_services(hass)