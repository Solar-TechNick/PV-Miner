"""Number platform for PV Miner integration."""
import logging
from typing import Any, Dict, Optional

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .luxos_api import LuxOSAPIError

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PV Miner number entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]
    config = hass.data[DOMAIN][config_entry.entry_id]["config"]
    
    entities = []
    
    # Power limit control
    entities.append(
        PVMinerPowerLimit(
            coordinator,
            api,
            config_entry.entry_id,
            config[CONF_NAME],
        )
    )
    
    # Manual frequency control
    entities.append(
        PVMinerFrequency(
            coordinator,
            api,
            config_entry.entry_id,
            config[CONF_NAME],
        )
    )
    
    # Solar power input
    entities.append(
        PVMinerSolarPower(
            coordinator,
            api,
            config_entry.entry_id,
            config[CONF_NAME],
        )
    )
    
    async_add_entities(entities)


class PVMinerPowerLimit(CoordinatorEntity, NumberEntity):
    """Number entity for power limit control."""

    def __init__(
        self,
        coordinator,
        api,
        config_entry_id: str,
        miner_name: str,
    ) -> None:
        """Initialize the power limit control."""
        super().__init__(coordinator)
        self._api = api
        self._config_entry_id = config_entry_id
        self._miner_name = miner_name
        
        self._attr_name = f"{miner_name} Power Limit"
        self._attr_unique_id = f"{config_entry_id}_power_limit"
        self._attr_icon = "mdi:flash"
        self._attr_native_unit_of_measurement = "W"
        self._attr_native_min_value = 500
        self._attr_native_max_value = 50000
        self._attr_native_step = 100

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
    def native_value(self) -> Optional[float]:
        """Return the current power limit."""
        if not self.coordinator.data or not self.coordinator.data.get("connected"):
            return None
            
        # This would come from the miner's current power configuration
        # For now, return a default value or extract from miner data
        data = self.coordinator.data
        stats = data.get("stats", {})
        if isinstance(stats, dict) and "STATS" in stats:
            stats_data = stats["STATS"]
            if isinstance(stats_data, list) and len(stats_data) > 1:
                miner_stats = stats_data[1]
                if "Power" in miner_stats:
                    return float(miner_stats["Power"])
        return 3000  # Default value

    async def async_set_native_value(self, value: float) -> None:
        """Set the power limit."""
        try:
            # This would involve setting power limits via LuxOS API
            # The exact command depends on how LuxOS handles power limiting
            _LOGGER.info("Setting power limit to %dW for miner %s", value, self._miner_name)
            
            # For now, we'll use frequency adjustment as a proxy for power control
            # Higher frequency = more power, lower frequency = less power
            # This is a simplified approach
            
            await self.coordinator.async_request_refresh()
        except LuxOSAPIError as e:
            _LOGGER.error("Error setting power limit: %s", e)
            raise


class PVMinerFrequency(CoordinatorEntity, NumberEntity):
    """Number entity for manual frequency control."""

    def __init__(
        self,
        coordinator,
        api,
        config_entry_id: str,
        miner_name: str,
    ) -> None:
        """Initialize the frequency control."""
        super().__init__(coordinator)
        self._api = api
        self._config_entry_id = config_entry_id
        self._miner_name = miner_name
        
        self._attr_name = f"{miner_name} Frequency Offset"
        self._attr_unique_id = f"{config_entry_id}_frequency"
        self._attr_icon = "mdi:speedometer"
        self._attr_native_min_value = -16
        self._attr_native_max_value = 4
        self._attr_native_step = 1

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
    def native_value(self) -> Optional[float]:
        """Return the current frequency offset."""
        if not self.coordinator.data or not self.coordinator.data.get("connected"):
            return None
        
        # Default to balanced (0 offset)
        return 0

    async def async_set_native_value(self, value: float) -> None:
        """Set the frequency offset."""
        try:
            await self._api.set_frequency(int(value))
            _LOGGER.info("Setting frequency offset to %d for miner %s", value, self._miner_name)
            await self.coordinator.async_request_refresh()
        except LuxOSAPIError as e:
            _LOGGER.error("Error setting frequency: %s", e)
            raise


class PVMinerSolarPower(CoordinatorEntity, NumberEntity):
    """Number entity for manual solar power input."""

    def __init__(
        self,
        coordinator,
        api,
        config_entry_id: str,
        miner_name: str,
    ) -> None:
        """Initialize the solar power input."""
        super().__init__(coordinator)
        self._api = api
        self._config_entry_id = config_entry_id
        self._miner_name = miner_name
        
        self._attr_name = f"{miner_name} Available Solar Power"
        self._attr_unique_id = f"{config_entry_id}_solar_power"
        self._attr_icon = "mdi:solar-power"
        self._attr_native_unit_of_measurement = "W"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 50000
        self._attr_native_step = 100

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
    def native_value(self) -> Optional[float]:
        """Return the available solar power."""
        # This could be linked to an external solar sensor
        # For now, return a stored value or default
        return getattr(self, '_solar_power', 0)

    async def async_set_native_value(self, value: float) -> None:
        """Set the available solar power."""
        self._solar_power = value
        _LOGGER.info("Available solar power set to %dW for miner %s", value, self._miner_name)
        
        # Trigger solar power management logic
        await self._handle_solar_power_change(value)

    async def _handle_solar_power_change(self, solar_power: float) -> None:
        """Handle changes in available solar power."""
        _LOGGER.debug("Handling solar power change: %dW", solar_power)
        
        # Basic solar power management logic
        if solar_power >= 4200:
            # Enough power for max performance
            await self._api.set_frequency(2)  # Max power profile
        elif solar_power >= 3000:
            # Enough power for balanced mode
            await self._api.set_frequency(0)  # Balanced profile
        elif solar_power >= 1500:
            # Enough power for eco mode
            await self._api.set_frequency(-8)  # Eco profile
        else:
            # Not enough power, go to standby
            await self._api.pause_mining()
        
        await self.coordinator.async_request_refresh()