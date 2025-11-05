"""Select platform for PV Miner integration."""
import logging
from typing import Any, Dict, List, Optional

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SOLAR_MODES
from .luxos_api import LuxOSAPIError

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PV Miner select entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]
    config = hass.data[DOMAIN][config_entry.entry_id]["config"]
    
    entities = []
    
    # Power profile selector
    power_profile_entity = PVMinerPowerProfile(
        coordinator,
        api,
        config_entry.entry_id,
        config[CONF_NAME],
    )
    
    # Update available profiles from miner
    try:
        await power_profile_entity.async_update_available_profiles()
    except Exception as e:
        _LOGGER.debug("Could not initialize profiles: %s", e)
    
    entities.append(power_profile_entity)
    
    # Solar operation mode selector
    entities.append(
        PVMinerSolarMode(
            coordinator,
            api,
            config_entry.entry_id,
            config[CONF_NAME],
        )
    )
    
    async_add_entities(entities)


class PVMinerPowerProfile(CoordinatorEntity, SelectEntity):
    """Select entity for power profile selection."""

    def __init__(
        self,
        coordinator,
        api,
        config_entry_id: str,
        miner_name: str,
    ) -> None:
        """Initialize the power profile selector."""
        super().__init__(coordinator)
        self._api = api
        self._config_entry_id = config_entry_id
        self._miner_name = miner_name
        self._current_profile = "default"  # Start with default profile
        self._available_profiles = ["default"]  # Will be updated dynamically
        self._profile_details = {}  # Store profile details for display
        
        self._attr_name = f"{miner_name} Power Profile"
        self._attr_unique_id = f"{config_entry_id}_power_profile"
        self._attr_icon = "mdi:speedometer"
        self._attr_options = self._available_profiles

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
    def current_option(self) -> Optional[str]:
        """Return the current power profile."""
        return self._current_profile

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        attributes = {}
        
        # Add current profile details if available
        if self._current_profile and self._current_profile in self._profile_details:
            details = self._profile_details[self._current_profile]
            attributes.update({
                "frequency_mhz": details.get("frequency"),
                "hashrate_ths": details.get("hashrate"),
                "power_watts": details.get("watts"),
                "voltage": details.get("voltage"),
                "step": details.get("step"),
                "description": details.get("description")
            })
        
        # Add summary of all available profiles
        if self._profile_details:
            profiles_summary = {}
            for name, details in self._profile_details.items():
                profiles_summary[name] = details.get("description", name)
            attributes["available_profiles"] = profiles_summary
            
        attributes["total_profiles"] = len(self._available_profiles)
        
        return attributes

    async def async_select_option(self, option: str) -> None:
        """Select a power profile."""
        if option not in self._available_profiles:
            _LOGGER.error("Invalid power profile: %s", option)
            return
        
        try:
            # Set profile for all boards (board=None means all boards)
            await self._api.set_profile(option)
            self._current_profile = option
            
            _LOGGER.info(
                "Set power profile '%s' for miner %s",
                option,
                self._miner_name
            )
            
            await self.coordinator.async_request_refresh()
        except LuxOSAPIError as e:
            _LOGGER.error("Error setting power profile: %s", e)
            raise

    async def async_update_available_profiles(self) -> None:
        """Update the list of available profiles from the miner."""
        try:
            # Get profile names
            profiles = await self._api.get_available_profiles()
            
            # Get detailed profile information
            profile_details = await self._api.get_all_profiles_with_details()
            
            if profiles and profile_details:
                self._available_profiles = profiles
                self._profile_details = profile_details
                self._attr_options = profiles
                
                _LOGGER.info(f"Updated {len(profiles)} dynamic profiles from miner")
                _LOGGER.debug("Available profiles: %s", profiles)
                
                # Log some example profile details
                for i, profile_name in enumerate(profiles[:3]):  # Show first 3
                    if profile_name in profile_details:
                        details = profile_details[profile_name]
                        _LOGGER.debug(f"  {profile_name}: {details['description']}")
                        
            elif profiles:
                # Fallback: just use profile names without details
                self._available_profiles = profiles
                self._attr_options = profiles
                _LOGGER.info(f"Updated {len(profiles)} profiles (no details available)")
                
        except Exception as e:
            _LOGGER.warning("Could not update available profiles: %s", e)
            # Keep default profiles if API call fails


class PVMinerSolarMode(CoordinatorEntity, SelectEntity):
    """Select entity for solar operation mode."""

    def __init__(
        self,
        coordinator,
        api,
        config_entry_id: str,
        miner_name: str,
    ) -> None:
        """Initialize the solar mode selector."""
        super().__init__(coordinator)
        self._api = api
        self._config_entry_id = config_entry_id
        self._miner_name = miner_name
        self._current_mode = "manual"
        
        self._attr_name = f"{miner_name} Solar Mode"
        self._attr_unique_id = f"{config_entry_id}_solar_mode"
        self._attr_icon = "mdi:solar-power"
        self._attr_options = list(SOLAR_MODES.keys())

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
    def current_option(self) -> Optional[str]:
        """Return the current solar mode."""
        return self._current_mode

    async def async_select_option(self, option: str) -> None:
        """Select a solar operation mode."""
        if option not in SOLAR_MODES:
            _LOGGER.error("Invalid solar mode: %s", option)
            return
        
        self._current_mode = option
        mode_name = SOLAR_MODES[option]
        
        _LOGGER.info(
            "Set solar mode '%s' for miner %s",
            mode_name,
            self._miner_name
        )
        
        # Here you would implement the logic for each solar mode
        if option == "manual":
            # Manual mode - user controls power via number entity
            pass
        elif option == "auto":
            # Auto mode - automatically adjust based on solar sensors
            await self._enable_auto_solar_tracking()
        elif option == "sun_curve":
            # Sun curve mode - follow sun pattern
            await self._enable_sun_curve_mode()
        elif option == "peak_solar":
            # Peak solar mode - 120% power during peak sun
            await self._enable_peak_solar_mode()

    async def _enable_auto_solar_tracking(self):
        """Enable automatic solar power tracking."""
        # Implementation for automatic solar tracking
        _LOGGER.info("Enabled automatic solar tracking for %s", self._miner_name)

    async def _enable_sun_curve_mode(self):
        """Enable sun curve following mode."""
        # Implementation for sun curve mode
        _LOGGER.info("Enabled sun curve mode for %s", self._miner_name)

    async def _enable_peak_solar_mode(self):
        """Enable peak solar mode with 120% power."""
        # Implementation for peak solar mode
        _LOGGER.info("Enabled peak solar mode for %s", self._miner_name)