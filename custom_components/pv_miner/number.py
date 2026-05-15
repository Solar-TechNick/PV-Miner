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

    entities = [
        PVMinerPowerLimit(
            coordinator,
            api,
            config_entry.entry_id,
            config[CONF_NAME],
        ),
        PVMinerSolarPower(
            coordinator,
            api,
            config_entry.entry_id,
            config[CONF_NAME],
        ),
    ]

    async_add_entities(entities)


class PVMinerPowerLimit(CoordinatorEntity, NumberEntity):
    """Number entity for power limit display."""

    def __init__(
        self,
        coordinator,
        api,
        config_entry_id: str,
        miner_name: str,
    ) -> None:
        """Initialize the power limit display."""
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
        """Return the current power draw reported by the miner."""
        if not self.coordinator.data or not self.coordinator.data.get("connected"):
            return None

        data = self.coordinator.data
        stats = data.get("stats", {})
        if isinstance(stats, dict) and "STATS" in stats:
            stats_data = stats["STATS"]
            if isinstance(stats_data, list) and len(stats_data) > 1:
                miner_stats = stats_data[1]
                if "Power" in miner_stats:
                    return float(miner_stats["Power"])
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Power limit is read-only; use the Power Profile select entity to change power."""
        _LOGGER.warning(
            "Power Limit is read-only. Use the Power Profile select entity to change power on %s.",
            self._miner_name,
        )


class PVMinerSolarPower(CoordinatorEntity, NumberEntity):
    """Available solar power input — read by SolarPowerCoordinator in auto mode."""

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
        self._solar_power: float = 0

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
        return self._solar_power

    async def async_set_native_value(self, value: float) -> None:
        """Store the available solar power. SolarPowerCoordinator picks this up in auto mode."""
        self._solar_power = value
        self.async_write_ha_state()
        _LOGGER.info("Available solar power set to %dW for miner %s", value, self._miner_name)
