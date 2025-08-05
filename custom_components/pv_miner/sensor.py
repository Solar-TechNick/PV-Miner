"""Sensor platform for PV Miner integration."""
import logging
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SENSOR_TYPES

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PV Miner sensor entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    config = hass.data[DOMAIN][config_entry.entry_id]["config"]
    
    entities = []
    
    # Create sensor entities
    for sensor_type, sensor_config in SENSOR_TYPES.items():
        entities.append(
            PVMinerSensor(
                coordinator,
                config_entry.entry_id,
                config[CONF_NAME],
                sensor_type,
                sensor_config,
            )
        )
    
    # Add hashboard-specific temperature sensors
    for board_num in range(3):  # Antminers typically have 3 hashboards
        entities.append(
            PVMinerHashboardSensor(
                coordinator,
                config_entry.entry_id,
                config[CONF_NAME],
                f"hashboard_{board_num}_temp",
                f"Hashboard {board_num} Temperature",
                board_num,
            )
        )
    
    async_add_entities(entities)


class PVMinerSensor(CoordinatorEntity, SensorEntity):
    """Representation of a PV Miner sensor."""

    def __init__(
        self,
        coordinator,
        config_entry_id: str,
        miner_name: str,
        sensor_type: str,
        sensor_config: Dict[str, Any],
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._config_entry_id = config_entry_id
        self._miner_name = miner_name
        self._sensor_type = sensor_type
        self._sensor_config = sensor_config
        
        self._attr_name = f"{miner_name} {sensor_config['name']}"
        self._attr_unique_id = f"{config_entry_id}_{sensor_type}"
        self._attr_icon = sensor_config.get("icon")
        self._attr_native_unit_of_measurement = sensor_config.get("unit")
        
        # Set state class for numeric sensors
        if sensor_config.get("unit") in ["TH/s", "W", "°C", "RPM", "J/TH", "s"]:
            self._attr_state_class = SensorStateClass.MEASUREMENT

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
    def native_value(self) -> Optional[Any]:
        """Return the state of the sensor."""
        if not self.coordinator.data or not self.coordinator.data.get("connected"):
            return None
            
        data = self.coordinator.data
        
        try:
            if self._sensor_type == "hashrate":
                return self._extract_hashrate(data)
            elif self._sensor_type == "power":
                return self._extract_power(data)
            elif self._sensor_type == "temperature":
                return self._extract_temperature(data)
            elif self._sensor_type == "fan_speed":
                return self._extract_fan_speed(data)
            elif self._sensor_type == "efficiency":
                return self._extract_efficiency(data)
            elif self._sensor_type == "uptime":
                return self._extract_uptime(data)
            elif self._sensor_type == "pool":
                return self._extract_pool(data)
        except (KeyError, TypeError, ValueError) as e:
            _LOGGER.debug("Error extracting %s: %s", self._sensor_type, e)
            return None

    def _extract_hashrate(self, data: Dict[str, Any]) -> Optional[float]:
        """Extract hashrate from miner data."""
        stats = data.get("stats", {})
        if isinstance(stats, dict) and "STATS" in stats:
            stats_data = stats["STATS"]
            if isinstance(stats_data, list) and len(stats_data) > 1:
                miner_stats = stats_data[1]
                if "GHS 5s" in miner_stats:
                    # Convert GH/s to TH/s
                    return round(float(miner_stats["GHS 5s"]) / 1000, 2)
        return None

    def _extract_power(self, data: Dict[str, Any]) -> Optional[int]:
        """Extract power consumption from miner data."""
        # Power data is in the separate power command
        power = data.get("power", {})
        if isinstance(power, dict) and "POWER" in power:
            power_data = power["POWER"]
            if isinstance(power_data, list) and len(power_data) > 0:
                power_info = power_data[0]
                if "Watts" in power_info:
                    return int(power_info["Watts"])
        return None

    def _extract_temperature(self, data: Dict[str, Any]) -> Optional[float]:
        """Extract average temperature from miner data."""
        # Use temp_max from stats for overall temperature
        stats = data.get("stats", {})
        if isinstance(stats, dict) and "STATS" in stats:
            stats_data = stats["STATS"]
            if isinstance(stats_data, list) and len(stats_data) > 1:
                miner_stats = stats_data[1]
                if "temp_max" in miner_stats:
                    return float(miner_stats["temp_max"])
        return None

    def _extract_fan_speed(self, data: Dict[str, Any]) -> Optional[int]:
        """Extract average fan speed from miner data."""
        # Use fans data for more accurate fan speeds
        fans = data.get("fans", {})
        if isinstance(fans, dict) and "FANS" in fans:
            fan_data = fans["FANS"]
            if isinstance(fan_data, list) and len(fan_data) > 0:
                total_rpm = 0
                count = 0
                for fan_info in fan_data:
                    if isinstance(fan_info, dict) and "RPM" in fan_info:
                        total_rpm += int(fan_info["RPM"])
                        count += 1
                if count > 0:
                    return round(total_rpm / count)
        
        # Fallback to stats data
        stats = data.get("stats", {})
        if isinstance(stats, dict) and "STATS" in stats:
            stats_data = stats["STATS"]
            if isinstance(stats_data, list) and len(stats_data) > 1:
                miner_stats = stats_data[1]
                # Get average of fan1-fan4
                fan_speeds = []
                for i in range(1, 5):
                    fan_key = f"fan{i}"
                    if fan_key in miner_stats and miner_stats[fan_key] > 0:
                        fan_speeds.append(int(miner_stats[fan_key]))
                if fan_speeds:
                    return round(sum(fan_speeds) / len(fan_speeds))
        return None

    def _extract_efficiency(self, data: Dict[str, Any]) -> Optional[float]:
        """Calculate efficiency (J/TH) from power and hashrate."""
        power = self._extract_power(data)
        hashrate = self._extract_hashrate(data)
        
        if power and hashrate and hashrate > 0:
            # J/TH = W / TH/s
            return round(power / hashrate, 2)
        return None

    def _extract_uptime(self, data: Dict[str, Any]) -> Optional[int]:
        """Extract uptime from miner data."""
        stats = data.get("stats", {})
        if isinstance(stats, dict) and "STATS" in stats:
            stats_data = stats["STATS"]
            if isinstance(stats_data, list) and len(stats_data) > 1:
                miner_stats = stats_data[1]
                if "Elapsed" in miner_stats:
                    return int(miner_stats["Elapsed"])
        return None

    def _extract_pool(self, data: Dict[str, Any]) -> Optional[str]:
        """Extract current mining pool from miner data."""
        pools = data.get("pools", {})
        if isinstance(pools, dict) and "POOLS" in pools:
            pool_data = pools["POOLS"]
            if isinstance(pool_data, list):
                for pool in pool_data:
                    if isinstance(pool, dict) and pool.get("Stratum Active"):
                        return pool.get("URL", "Unknown")
        return None


class PVMinerHashboardSensor(CoordinatorEntity, SensorEntity):
    """Representation of a hashboard temperature sensor."""

    def __init__(
        self,
        coordinator,
        config_entry_id: str,
        miner_name: str,
        sensor_type: str,
        sensor_name: str,
        board_num: int,
    ) -> None:
        """Initialize the hashboard sensor."""
        super().__init__(coordinator)
        self._config_entry_id = config_entry_id
        self._miner_name = miner_name
        self._sensor_type = sensor_type
        self._board_num = board_num
        
        self._attr_name = f"{miner_name} {sensor_name}"
        self._attr_unique_id = f"{config_entry_id}_{sensor_type}"
        self._attr_icon = "mdi:thermometer"
        self._attr_native_unit_of_measurement = "°C"
        self._attr_state_class = SensorStateClass.MEASUREMENT

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
        """Return the hashboard temperature."""
        if not self.coordinator.data or not self.coordinator.data.get("connected"):
            return None
        
        # Use DEVS data for individual hashboard temperatures
        devs = self.coordinator.data.get("devs", {})
        if isinstance(devs, dict) and "DEVS" in devs:
            dev_data = devs["DEVS"]
            if isinstance(dev_data, list):
                for dev in dev_data:
                    if isinstance(dev, dict) and dev.get("ASC") == self._board_num:
                        if "Temperature" in dev:
                            return float(dev["Temperature"])
        
        # Fallback to stats data
        stats = self.coordinator.data.get("stats", {})
        if isinstance(stats, dict) and "STATS" in stats:
            stats_data = stats["STATS"]
            if isinstance(stats_data, list) and len(stats_data) > 1:
                miner_stats = stats_data[1]
                temp_key = f"temp{self._board_num + 1}"  # temp1, temp2, temp3
                if temp_key in miner_stats:
                    return float(miner_stats[temp_key])
        
        return None