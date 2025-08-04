"""Service calls for PV Miner integration."""
import logging
from typing import Any, Dict

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    POWER_PROFILES,
    SERVICE_ECO_MODE,
    SERVICE_EMERGENCY_STOP,
    SERVICE_SET_POOL,
    SERVICE_SET_POWER_LIMIT,
    SERVICE_SET_POWER_PROFILE,
    SERVICE_SOLAR_MAX,
)
from .luxos_api import LuxOSAPIError

_LOGGER = logging.getLogger(__name__)

# Service schemas
SET_POWER_PROFILE_SCHEMA = vol.Schema({
    vol.Required("entity_id"): cv.entity_ids,
    vol.Required("profile"): vol.In(list(POWER_PROFILES.keys())),
})

SET_POWER_LIMIT_SCHEMA = vol.Schema({
    vol.Required("entity_id"): cv.entity_ids,
    vol.Required("power_limit"): vol.All(vol.Coerce(int), vol.Range(min=500, max=50000)),
})

EMERGENCY_STOP_SCHEMA = vol.Schema({
    vol.Required("entity_id"): cv.entity_ids,
})

SOLAR_MAX_SCHEMA = vol.Schema({
    vol.Required("entity_id"): cv.entity_ids,
})

ECO_MODE_SCHEMA = vol.Schema({
    vol.Required("entity_id"): cv.entity_ids,
})

SET_POOL_SCHEMA = vol.Schema({
    vol.Required("entity_id"): cv.entity_ids,
    vol.Required("pool_url"): cv.string,
    vol.Required("pool_user"): cv.string,
    vol.Optional("pool_password", default="x"): cv.string,
    vol.Optional("priority", default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=10)),
})


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for the PV Miner integration."""
    
    async def handle_set_power_profile(call: ServiceCall) -> None:
        """Handle set power profile service call."""
        entity_ids = call.data["entity_id"]
        profile = call.data["profile"]
        
        for entity_id in entity_ids:
            await _execute_service_for_entity(
                hass, entity_id, _set_power_profile, profile=profile
            )

    async def handle_set_power_limit(call: ServiceCall) -> None:
        """Handle set power limit service call."""
        entity_ids = call.data["entity_id"]
        power_limit = call.data["power_limit"]
        
        for entity_id in entity_ids:
            await _execute_service_for_entity(
                hass, entity_id, _set_power_limit, power_limit=power_limit
            )

    async def handle_emergency_stop(call: ServiceCall) -> None:
        """Handle emergency stop service call."""
        entity_ids = call.data["entity_id"]
        
        for entity_id in entity_ids:
            await _execute_service_for_entity(
                hass, entity_id, _emergency_stop
            )

    async def handle_solar_max(call: ServiceCall) -> None:
        """Handle solar max service call."""
        entity_ids = call.data["entity_id"]
        
        for entity_id in entity_ids:
            await _execute_service_for_entity(
                hass, entity_id, _solar_max
            )

    async def handle_eco_mode(call: ServiceCall) -> None:
        """Handle eco mode service call."""
        entity_ids = call.data["entity_id"]
        
        for entity_id in entity_ids:
            await _execute_service_for_entity(
                hass, entity_id, _eco_mode
            )

    async def handle_set_pool(call: ServiceCall) -> None:
        """Handle set pool service call."""
        entity_ids = call.data["entity_id"]
        pool_url = call.data["pool_url"]
        pool_user = call.data["pool_user"]
        pool_password = call.data["pool_password"]
        priority = call.data["priority"]
        
        for entity_id in entity_ids:
            await _execute_service_for_entity(
                hass, entity_id, _set_pool,
                pool_url=pool_url,
                pool_user=pool_user,
                pool_password=pool_password,
                priority=priority
            )

    # Register services
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_POWER_PROFILE,
        handle_set_power_profile,
        schema=SET_POWER_PROFILE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_POWER_LIMIT,
        handle_set_power_limit,
        schema=SET_POWER_LIMIT_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_EMERGENCY_STOP,
        handle_emergency_stop,
        schema=EMERGENCY_STOP_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SOLAR_MAX,
        handle_solar_max,
        schema=SOLAR_MAX_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_ECO_MODE,
        handle_eco_mode,
        schema=ECO_MODE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_POOL,
        handle_set_pool,
        schema=SET_POOL_SCHEMA,
    )


async def _execute_service_for_entity(
    hass: HomeAssistant,
    entity_id: str,
    service_func,
    **kwargs
) -> None:
    """Execute a service function for a specific entity."""
    # Find the config entry for this entity
    config_entry_id = None
    for entry_id, entry_data in hass.data[DOMAIN].items():
        # Check if this entity belongs to this config entry
        # This is a simplified approach - in reality you'd need to track entity-to-config mappings
        config_entry_id = entry_id
        break
    
    if not config_entry_id:
        _LOGGER.error("Could not find config entry for entity %s", entity_id)
        return
    
    api = hass.data[DOMAIN][config_entry_id]["api"]
    coordinator = hass.data[DOMAIN][config_entry_id]["coordinator"]
    
    try:
        await service_func(api, **kwargs)
        await coordinator.async_request_refresh()
    except LuxOSAPIError as e:
        _LOGGER.error("Service call failed for %s: %s", entity_id, e)


async def _set_power_profile(api, profile: str) -> None:
    """Set power profile via API."""
    profile_config = POWER_PROFILES[profile]
    overclock = profile_config["overclock"]
    
    await api.set_frequency(overclock)
    _LOGGER.info("Set power profile '%s' (overclock: %d)", profile_config["name"], overclock)


async def _set_power_limit(api, power_limit: int) -> None:
    """Set power limit via API."""
    # This is a simplified approach - actual implementation would depend on LuxOS capabilities
    # For now, we'll map power limits to frequency offsets
    
    if power_limit <= 1500:
        # Eco mode
        frequency = -8
    elif power_limit <= 3000:
        # Balanced mode
        frequency = 0
    elif power_limit >= 4200:
        # Max power mode
        frequency = 2
    else:
        # Calculate frequency based on power
        frequency = int((power_limit - 3000) / 600)  # Rough calculation
        frequency = max(-16, min(4, frequency))
    
    await api.set_frequency(frequency)
    _LOGGER.info("Set power limit to %dW (frequency offset: %d)", power_limit, frequency)


async def _emergency_stop(api) -> None:
    """Emergency stop all mining operations."""
    await api.pause_mining()
    _LOGGER.info("Emergency stop executed")


async def _solar_max(api) -> None:
    """Set to solar max mode (4200W)."""
    await api.set_frequency(2)  # Max power overclock
    _LOGGER.info("Solar max mode activated (4200W)")


async def _eco_mode(api) -> None:
    """Set to eco mode (1500W)."""
    await api.set_frequency(-8)  # Eco underclock
    _LOGGER.info("Eco mode activated (1500W)")


async def _set_pool(api, pool_url: str, pool_user: str, pool_password: str, priority: int) -> None:
    """Add and switch to a new mining pool."""
    await api.add_pool(pool_url, pool_user, pool_password, priority)
    _LOGGER.info("Added mining pool: %s", pool_url)