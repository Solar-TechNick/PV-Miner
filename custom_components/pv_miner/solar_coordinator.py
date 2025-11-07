"""Solar power coordinator for automatic miner power adjustment."""
import logging
from datetime import timedelta
from typing import Optional

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Power profile mapping: available solar power (W) -> LuxOS profile name
# Uses all profiles from -16 (260MHz) to +1 (685MHz)
POWER_PROFILE_MAP = [
    (0, "260MHz"),      # 0-2300W: Profile -16 (Min: 2223W, 48 TH/s)
    (2300, "285MHz"),   # 2300-2400W: Profile -15
    (2400, "310MHz"),   # 2400-2500W: Profile -14
    (2500, "335MHz"),   # 2500-2600W: Profile -12
    (2600, "360MHz"),   # 2600-2700W: Profile -10
    (2700, "385MHz"),   # 2700-2800W: Profile -8 (Low)
    (2800, "410MHz"),   # 2800-2900W: Profile -7
    (2900, "435MHz"),   # 2900-3000W: Profile -5
    (3000, "460MHz"),   # 3000-3100W: Profile -6
    (3100, "485MHz"),   # 3100-3200W: Profile -4
    (3200, "510MHz"),   # 3200-3300W: Profile -3 (Mid)
    (3300, "535MHz"),   # 3300-3400W: Profile -2
    (3400, "560MHz"),   # 3400-3500W: Profile -1
    (3500, "585MHz"),   # 3500-3600W: Profile -2
    (3600, "610MHz"),   # 3600-3700W: Profile -1
    (3700, "635MHz"),   # 3700-3800W: Profile 0
    (3800, "660MHz"),   # 3800-3900W: Profile 0
    (3900, "685MHz"),   # 3900W+: Profile +1 (Max: 3693W, 127 TH/s)
]


class SolarPowerCoordinator:
    """Coordinator for automatic solar power adjustment."""

    def __init__(
        self,
        hass: HomeAssistant,
        api,
        config_entry_id: str,
        miner_name: str,
        solar_sensor: str = "sensor.pro3em_total_active_power",
    ) -> None:
        """Initialize the solar power coordinator."""
        self.hass = hass
        self._api = api
        self._config_entry_id = config_entry_id
        self._miner_name = miner_name
        self._solar_sensor = solar_sensor
        self._current_profile = None
        self._is_auto_mode = False
        self._update_interval = timedelta(seconds=30)
        self._cancel_update = None

    async def async_start(self) -> None:
        """Start the solar power coordinator."""
        _LOGGER.info(
            "Starting solar power coordinator for %s (monitoring %s)",
            self._miner_name,
            self._solar_sensor,
        )

        # Start periodic updates
        self._cancel_update = async_track_time_interval(
            self.hass,
            self._async_update,
            self._update_interval,
        )

    async def async_stop(self) -> None:
        """Stop the solar power coordinator."""
        if self._cancel_update:
            self._cancel_update()
            self._cancel_update = None

    def set_auto_mode(self, enabled: bool) -> None:
        """Enable or disable auto mode."""
        self._is_auto_mode = enabled
        _LOGGER.info(
            "Auto mode %s for %s",
            "enabled" if enabled else "disabled",
            self._miner_name,
        )

    async def _async_update(self, now=None) -> None:
        """Update miner power based on solar production."""
        if not self._is_auto_mode:
            return

        try:
            # Get solar production from sensor
            solar_state = self.hass.states.get(self._solar_sensor)

            if solar_state is None:
                _LOGGER.warning(
                    "Solar sensor %s not found - auto mode disabled",
                    self._solar_sensor,
                )
                return

            try:
                solar_power = float(solar_state.state)
            except (ValueError, TypeError):
                _LOGGER.warning(
                    "Invalid solar power value: %s",
                    solar_state.state,
                )
                return

            # Get available solar power entity value
            available_solar_entity = f"number.{self._miner_name.lower().replace(' ', '_')}_available_solar_power"
            available_state = self.hass.states.get(available_solar_entity)

            # Use available solar power if set, otherwise use total solar production
            if available_state and available_state.state not in ("unknown", "unavailable"):
                try:
                    available_power = float(available_state.state)
                except (ValueError, TypeError):
                    available_power = solar_power
            else:
                available_power = solar_power

            # Check if we should sleep the miner (no solar power)
            if available_power < 500:
                # Not enough solar power - put miner to sleep
                if self._current_profile != "sleep":
                    _LOGGER.info(
                        "Auto-sleeping %s: %.0fW solar (insufficient power)",
                        self._miner_name,
                        available_power,
                    )
                    try:
                        await self._api.pause_mining()
                        self._current_profile = "sleep"
                    except Exception as e:
                        _LOGGER.error("Failed to sleep miner: %s", e)
                return

            # Determine appropriate power profile
            target_profile = self._get_profile_for_power(available_power)

            # Wake miner if it's currently asleep
            if self._current_profile == "sleep":
                _LOGGER.info(
                    "Auto-waking %s: %.0fW solar available",
                    self._miner_name,
                    available_power,
                )
                try:
                    await self._api.resume_mining()
                    # Give miner time to wake up before setting profile
                    import asyncio
                    await asyncio.sleep(5)
                except Exception as e:
                    _LOGGER.error("Failed to wake miner: %s", e)
                    return

            # Only change profile if different from current
            if target_profile != self._current_profile:
                _LOGGER.info(
                    "Auto-adjusting %s: %.0fW solar -> profile %s (was %s)",
                    self._miner_name,
                    available_power,
                    target_profile,
                    self._current_profile or "unknown",
                )

                # Set the power profile via API
                try:
                    await self._api.set_profile(target_profile)
                    self._current_profile = target_profile
                except Exception as e:
                    _LOGGER.error(
                        "Failed to set power profile %s: %s",
                        target_profile,
                        e,
                    )

        except Exception as e:
            _LOGGER.error("Error in solar power coordinator update: %s", e)

    def _get_profile_for_power(self, available_power: float) -> str:
        """Get the appropriate power profile for available solar power."""
        # Note: Caller should check for < 100W and handle sleep separately

        # Find the appropriate profile from the map
        for i, (threshold, profile) in enumerate(POWER_PROFILE_MAP):
            # If this is the last entry or power is below next threshold
            if i == len(POWER_PROFILE_MAP) - 1:
                return profile

            next_threshold = POWER_PROFILE_MAP[i + 1][0]
            if available_power < next_threshold:
                return profile

        # Fallback to max profile
        return "685MHz"
