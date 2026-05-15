"""Service calls for PV Miner integration."""
import logging

import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import (
    DOMAIN,
    SERVICE_EMERGENCY_STOP,
    SERVICE_SET_POOL,
    SERVICE_SET_POWER_PROFILE,
    SERVICE_SLEEP_MINER,
    SERVICE_WAKE_MINER,
)
from .luxos_api import LuxOSAPIError

_LOGGER = logging.getLogger(__name__)

# Service schemas
SET_POWER_PROFILE_SCHEMA = vol.Schema({
    vol.Required("entity_id"): cv.entity_ids,
    vol.Required("profile"): cv.string,  # Accept any valid profile name dynamically
})

EMERGENCY_STOP_SCHEMA = vol.Schema({
    vol.Required("entity_id"): cv.entity_ids,
})

SET_POOL_SCHEMA = vol.Schema({
    vol.Required("entity_id"): cv.entity_ids,
    vol.Required("pool_url"): cv.string,
    vol.Required("pool_user"): cv.string,
    vol.Optional("pool_password", default="x"): cv.string,
    vol.Optional("priority", default=0): vol.All(vol.Coerce(int), vol.Range(min=0, max=10)),
})

SLEEP_MINER_SCHEMA = vol.Schema({
    vol.Required("entity_id"): cv.entity_ids,
})

WAKE_MINER_SCHEMA = vol.Schema({
    vol.Required("entity_id"): cv.entity_ids,
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

    async def handle_emergency_stop(call: ServiceCall) -> None:
        """Handle emergency stop service call."""
        entity_ids = call.data["entity_id"]

        for entity_id in entity_ids:
            await _execute_service_for_entity(
                hass, entity_id, _emergency_stop
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

    async def handle_sleep_miner(call: ServiceCall) -> None:
        """Handle sleep miner service call."""
        entity_ids = call.data["entity_id"]

        for entity_id in entity_ids:
            await _execute_service_for_entity(
                hass, entity_id, _sleep_miner
            )

    async def handle_wake_miner(call: ServiceCall) -> None:
        """Handle wake miner service call."""
        entity_ids = call.data["entity_id"]

        for entity_id in entity_ids:
            await _execute_service_for_entity(
                hass, entity_id, _wake_miner
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
        SERVICE_EMERGENCY_STOP,
        handle_emergency_stop,
        schema=EMERGENCY_STOP_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_POOL,
        handle_set_pool,
        schema=SET_POOL_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_SLEEP_MINER,
        handle_sleep_miner,
        schema=SLEEP_MINER_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_WAKE_MINER,
        handle_wake_miner,
        schema=WAKE_MINER_SCHEMA,
    )


async def _execute_service_for_entity(
    hass: HomeAssistant,
    entity_id: str,
    service_func,
    **kwargs
) -> None:
    """Execute a service function for a specific entity."""
    from homeassistant.helpers import entity_registry as er

    entity_registry = er.async_get(hass)
    entity_entry = entity_registry.async_get(entity_id)

    if not entity_entry:
        _LOGGER.error("Entity %s not found in registry", entity_id)
        return

    config_entry_id = entity_entry.config_entry_id

    if not config_entry_id or config_entry_id not in hass.data.get(DOMAIN, {}):
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
    """Set power profile via API using dynamic LuxOS profiles."""
    try:
        await api.set_profile(profile)
        _LOGGER.info("Set power profile to '%s'", profile)
    except Exception as e:
        _LOGGER.error("Failed to set power profile '%s': %s", profile, e)
        raise


async def _emergency_stop(api) -> None:
    """Emergency stop all mining operations."""
    await api.pause_mining()
    _LOGGER.info("Emergency stop executed")


async def _set_pool(api, pool_url: str, pool_user: str, pool_password: str, priority: int) -> None:
    """Add and switch to a new mining pool."""
    await api.add_pool(pool_url, pool_user, pool_password, priority)
    _LOGGER.info("Added mining pool: %s", pool_url)


async def _sleep_miner(api) -> None:
    """Put the miner into sleep mode (curtail sleep)."""
    await api.pause_mining()
    _LOGGER.info("Miner put into sleep mode (curtail sleep)")


async def _wake_miner(api) -> None:
    """Wake up the miner from sleep mode (curtail wakeup)."""
    await api.resume_mining()
    _LOGGER.info("Miner woken up from sleep mode (curtail wakeup)")
