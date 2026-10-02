"""Sensor platform for LIFAair."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature, CONCENTRATION_PARTS_PER_MILLION, CONCENTRATION_MICROGRAMS_PER_CUBIC_METER
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_CO2,
    ATTR_HUMIDITY,
    ATTR_PM1,
    ATTR_PM10,
    ATTR_PM25,
    ATTR_TEMPERATURE,
    ATTR_TVOC,
    DOMAIN,
)
from .coordinator import LifaAirCoordinator


@dataclass(frozen=True)
class SensorDescription:
    key: str
    name: str
    device_class: SensorDeviceClass | None
    unit: str
    state_class: SensorStateClass | None


SENSORS = (
    SensorDescription(
        ATTR_TEMPERATURE,
        "Temperature",
        SensorDeviceClass.TEMPERATURE,
        UnitOfTemperature.CELSIUS,
        SensorStateClass.MEASUREMENT,
    ),
    SensorDescription(
        ATTR_HUMIDITY,
        "Humidity",
        SensorDeviceClass.HUMIDITY,
        PERCENTAGE,
        SensorStateClass.MEASUREMENT,
    ),
    SensorDescription(
        ATTR_CO2,
        "CO2",
        SensorDeviceClass.CO2,
        CONCENTRATION_PARTS_PER_MILLION,
        SensorStateClass.MEASUREMENT,
    ),
    SensorDescription(
        ATTR_TVOC,
        "TVOC",
        None,
        "µg/m³",
        SensorStateClass.MEASUREMENT,
    ),
    SensorDescription(
        ATTR_PM1,
        "PM1",
        None,
        "µg/m³",
        SensorStateClass.MEASUREMENT,
    ),
    SensorDescription(
        ATTR_PM25,
        "PM2.5",
        SensorDeviceClass.PM25,
        CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        SensorStateClass.MEASUREMENT,
    ),
    SensorDescription(
        ATTR_PM10,
        "PM10",
        SensorDeviceClass.PM10,
        CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up LIFAair sensors."""
    coordinator: LifaAirCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        LifaAirSensor(coordinator, entry, description) for description in SENSORS
    )


class LifaAirSensor(CoordinatorEntity[LifaAirCoordinator], SensorEntity):
    """Representation of a LIFAair sensor."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: LifaAirCoordinator,
        entry: ConfigEntry,
        description: SensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.device.mac.hex()}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.device.mac.hex())},
            "name": coordinator.device.name or "LIFAair",
            "manufacturer": "LIFAair",
            "model": "LIFAair",
        }

    @property
    def native_value(self):
        """Return the current sensor value."""
        return self.coordinator.data.get(self.entity_description.key)
