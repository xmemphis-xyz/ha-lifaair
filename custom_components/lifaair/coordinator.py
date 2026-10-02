"""Coordinator for LIFAair."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import LifaAirDevice
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class LifaAirCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate LIFAair state updates."""

    def __init__(self, hass: HomeAssistant, device: LifaAirDevice) -> None:
        """Initialize the coordinator."""
        self.device = device
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
            update_method=self._async_update_data,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch state from the purifier."""
        try:
            return await self.hass.async_add_executor_job(self.device.get_state)
        except Exception as err:
            raise UpdateFailed(f"Unable to communicate with LIFAair: {err}") from err
