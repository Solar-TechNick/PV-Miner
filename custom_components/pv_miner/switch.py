"""Switch platform for PV Miner integration."""
import logging
from typing import Any, Dict, Optional

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SWITCH_TYPES
from .luxos_api import LuxOSAPIError

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PV Miner switch entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]
    config = hass.data[DOMAIN][config_entry.entry_id]["config"]
    
    entities = []
    
    # Create main miner switch
    entities.append(
        PVMinerSwitch(
            coordinator,
            api,
            config_entry.entry_id,
            config[CONF_NAME],
            "miner_enabled",
            SWITCH_TYPES["miner_enabled"],
        )
    )

    # Hashboard switches removed - not supported by LuxOS firmware 2025.10.15.191043
    # Use power profile switching instead for granular power control

    async_add_entities(entities)


class PVMinerSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a PV Miner switch."""

    def __init__(
        self,
        coordinator,
        api,
        config_entry_id: str,
        miner_name: str,
        switch_type: str,
        switch_config: Dict[str, Any],
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._api = api
        self._config_entry_id = config_entry_id
        self._miner_name = miner_name
        self._switch_type = switch_type
        self._switch_config = switch_config
        
        self._attr_name = f"{miner_name} {switch_config['name']}"
        self._attr_unique_id = f"{config_entry_id}_{switch_type}"
        self._attr_icon = switch_config.get("icon")

    @property
    def device_info(self) -> Dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._config_entry_id)},
            "name": self._miner_name,
            "manufacturer": "Antminer",
            "model": "Bitcoin Miner",
            "sw_version": "LuxOS",
        }

    @property
    def is_on(self) -> Optional[bool]:
        """Return True if the miner is on."""
        if not self.coordinator.data or not self.coordinator.data.get("connected"):
            return None
            
        data = self.coordinator.data
        
        try:
            if self._switch_type == "miner_enabled":
                return self._is_miner_enabled(data)
        except (KeyError, TypeError, ValueError) as e:
            _LOGGER.debug("Error checking switch state %s: %s", self._switch_type, e)
            return None

    def _is_miner_enabled(self, data: Dict[str, Any]) -> bool:
        """Check if miner is enabled based on hashrate."""
        stats = data.get("stats", {})
        if isinstance(stats, dict) and "STATS" in stats:
            stats_data = stats["STATS"]
            if isinstance(stats_data, list) and len(stats_data) > 1:
                miner_stats = stats_data[1]
                if "GHS 5s" in miner_stats:
                    hashrate = float(miner_stats["GHS 5s"])
                    # Consider the miner enabled if hashrate is above a reasonable threshold
                    # Curtailed/sleep mode may show very low hashrate (~20-50 TH/s instead of normal ~95 TH/s)
                    # Set threshold at 1000 GH/s (1 TH/s) to distinguish from curtailed state
                    return hashrate > 1000  # 1000 GH/s = 1 TH/s
        return False

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the miner on."""
        try:
            if self._switch_type == "miner_enabled":
                await self._api.resume_mining()
                _LOGGER.info("Miner %s turned on", self._miner_name)
        except LuxOSAPIError as e:
            _LOGGER.error("Error turning on miner %s: %s", self._miner_name, e)
            raise
        
        # Request coordinator refresh
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the miner off."""
        try:
            if self._switch_type == "miner_enabled":
                await self._api.pause_mining()
                _LOGGER.info("Miner %s turned off", self._miner_name)
        except LuxOSAPIError as e:
            _LOGGER.error("Error turning off miner %s: %s", self._miner_name, e)
            raise
        
        # Request coordinator refresh
        await self.coordinator.async_request_refresh()
# Hashboard switch class removed - enableboard/disableboard commands don't work
# in LuxOS firmware 2025.10.15.191043. Use power profile switching for control.