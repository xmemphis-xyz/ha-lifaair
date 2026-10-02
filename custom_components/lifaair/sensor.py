"""Sensor platform for LIFAair."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    UnitOfTemperature,
)
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


SENSORS = (
    SensorEntityDescription(
        key=ATTR_TEMPERATURE,
        name="Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_HUMIDITY,
        name="Humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_CO2,
        name="CO2",
        device_class=SensorDeviceClass.CO2,
        native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_TVOC,
        name="TVOC",
        native_unit_of_measurement="µg/m³",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_PM1,
        name="PM1",
        native_unit_of_measurement="µg/m³",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_PM25,
        name="PM2.5",
        device_class=SensorDeviceClass.PM25,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key=ATTR_PM10,
        name="PM10",
        device_class=SensorDeviceClass.PM10,
        native_unit_of_measurement=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
        state_class=SensorStateClass.MEASUREMENT,
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
        description: SensorEntityDescription,
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
