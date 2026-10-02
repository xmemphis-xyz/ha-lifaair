"""Fan platform for LIFAair."""

from __future__ import annotations

from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.percentage import percentage_to_ranged_value, ranged_value_to_percentage

from .api import FanMode
from .const import (
    DOMAIN,
    PRESET_ANTI_ALLERGY,
    PRESET_AUTO,
    PRESET_MANUAL,
    PRESET_NIGHT,
    PRESET_TURBO,
)
from .coordinator import LifaAirCoordinator

PRESET_TO_MODE = {
    PRESET_AUTO: FanMode.AUTO,
    PRESET_NIGHT: FanMode.NIGHT,
    PRESET_TURBO: FanMode.TURBO,
    PRESET_ANTI_ALLERGY: FanMode.ANTI_ALLERGY,
    PRESET_MANUAL: FanMode.MANUAL,
}

MODE_TO_PRESET = {value: key for key, value in PRESET_TO_MODE.items()}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the LIFAair fan."""
    coordinator: LifaAirCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LifaAirFan(coordinator, entry)])


class LifaAirFan(CoordinatorEntity[LifaAirCoordinator], FanEntity):
    """Representation of a LIFAair purifier fan."""

    _attr_has_entity_name = True
    _attr_name = "Purifier"
    _attr_supported_features = (
        FanEntityFeature.SET_SPEED
        | FanEntityFeature.PRESET_MODE
        | FanEntityFeature.TURN_ON
        | FanEntityFeature.TURN_OFF
    )
    _attr_preset_modes = list(PRESET_TO_MODE)
    _attr_speed_count = 121

    def __init__(
        self,
        coordinator: LifaAirCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the fan."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.device.mac.hex()}_fan"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.device.mac.hex())},
            "name": coordinator.device.name or "LIFAair",
            "manufacturer": "LIFAair",
            "model": "LIFAair",
        }

    @property
    def is_on(self) -> bool:
        """Return whether the purifier is on."""
        mode = self.coordinator.data.get("fan_mode")
        return mode not in (None, FanMode.OFF)

    @property
    def percentage(self) -> int | None:
        """Return the current fan speed percentage."""
        speed = self.coordinator.data.get("fan_speed")
        if speed is None:
            return None
        if speed == 0:
            return 0
        return ranged_value_to_percentage((1, 121), speed)

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        mode = self.coordinator.data.get("fan_mode")
        return MODE_TO_PRESET.get(mode)

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Turn the purifier on."""
        if preset_mode is not None:
            await self.async_set_preset_mode(preset_mode)
        elif percentage is not None and percentage > 0:
            await self.async_set_percentage(percentage)
        else:
            await self.async_set_preset_mode(PRESET_AUTO)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the purifier off."""
        await self.hass.async_add_executor_job(
            self.coordinator.device.set_fan_mode,
            FanMode.OFF,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the fan speed percentage."""
        if percentage <= 0:
            await self.async_turn_off()
            return

        speed = round(percentage_to_ranged_value((1, 121), percentage))
        await self.hass.async_add_executor_job(
            self.coordinator.device.set_fan_speed,
            speed,
        )
        await self.coordinator.async_request_refresh()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set the fan preset mode."""
        mode = PRESET_TO_MODE[preset_mode]
        await self.hass.async_add_executor_job(
            self.coordinator.device.set_fan_mode,
            mode,
        )
        await self.coordinator.async_request_refresh()
