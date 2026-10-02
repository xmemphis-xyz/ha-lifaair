"""Local protocol implementation for LIFAair devices."""

from __future__ import annotations

import enum
from typing import Any

import broadlink
from broadlink import exceptions as broadlink_exceptions


class FanMode(enum.IntEnum):
    """LIFAair fan modes."""

    OFF = 0
    AUTO = 1
    NIGHT = 2
    TURBO = 3
    ANTI_ALLERGY = 4
    MANUAL = 5
    UNKNOWN = -1


class LifaAirDevice(broadlink.Device):
    """Controls a LIFAair purifier using the Broadlink protocol."""

    TYPE = "LIFAAIR"

    FAN_STATE_TO_MODE = {
        0x81: FanMode.OFF,
        0xA5: FanMode.AUTO,
        0x95: FanMode.NIGHT,
        0x8D: FanMode.TURBO,
        0x85: FanMode.MANUAL,
        0x01: None,
    }

    class _Operation(enum.IntEnum):
        SET_STATE = 1
        GET_STATE = 2

    class _Action(enum.IntEnum):
        SET_FAN_SPEED = 1
        SET_FAN_MODE = 2

    FAN_MODE_TO_ACTION_ARG = {
        FanMode.OFF: 1,
        FanMode.AUTO: 2,
        FanMode.NIGHT: 6,
        FanMode.TURBO: 7,
        FanMode.ANTI_ALLERGY: 11,
    }

    @classmethod
    def connect(cls, host: str) -> "LifaAirDevice":
        """Discover and authenticate a LIFAair device at the given host."""
        discovered = broadlink.hello(host, port=80, timeout=5)

        if discovered.devtype != 0x4EC2:
            raise ValueError(
                f"Unsupported Broadlink device type: 0x{discovered.devtype:04x}"
            )

        device = cls(
            discovered.host,
            discovered.mac,
            discovered.devtype,
            timeout=5,
            name=discovered.name,
            model="LIFAair",
            manufacturer="LIFAair",
            is_locked=discovered.is_locked,
        )
        device.auth()
        return device

    def set_fan_mode(self, fan_mode: FanMode) -> dict[str, Any]:
        """Set the fan mode and return the updated state."""
        if fan_mode == FanMode.MANUAL:
            return self.set_fan_speed(50)

        action_arg = self.FAN_MODE_TO_ACTION_ARG.get(fan_mode)
        if action_arg is not None:
            data = self._send(
                self._Operation.SET_STATE,
                self._Action.SET_FAN_MODE,
                action_arg,
            )
            return self._decode_state(data)

        return self.get_state()

    def set_fan_speed(self, fan_speed: int) -> dict[str, Any]:
        """Set fan speed from 0 to 121."""
        if not 0 <= fan_speed <= 121:
            raise ValueError("Fan speed must be between 0 and 121")

        data = self._send(
            self._Operation.SET_STATE,
            self._Action.SET_FAN_SPEED,
            fan_speed,
        )
        return self._decode_state(data)

    def get_state(self) -> dict[str, Any]:
        """Return the current purifier state."""
        data = self._send(self._Operation.GET_STATE)
        return self._decode_state(data)

    def _decode_state(self, data: bytes) -> dict[str, Any]:
        """Decode a LIFAair state response."""
        raw = self._decode_state_raw(data)
        fan_mode = self._decode_fan_mode(raw["fan_state"], raw["fan_flags"])
        offline = fan_mode is None

        return {
            "temperature": None if offline else raw["temperature"] / 10.0,
            "humidity": None if offline else raw["humidity"],
            "co2": raw["co2"],
            "tvoc": raw["tvoc"] * 10,
            "pm10": raw["pm10"],
            "pm2_5": raw["pm2_5"],
            "pm1": raw["pm1"],
            "fan_mode": fan_mode,
            "fan_speed": raw["fan_speed"],
        }

    @staticmethod
    def _decode_state_raw(data: bytes) -> dict[str, int]:
        """Decode raw state bytes."""
        return {
            "temperature": data[27] + 256 * data[28],
            "humidity": data[29],
            "co2": data[31] + 256 * data[32],
            "tvoc": data[35] + 256 * data[36],
            "pm10": data[37] + 256 * data[38],
            "pm2_5": data[39] + 256 * data[40],
            "pm1": data[41] + 256 * data[42],
            "fan_state": data[55],
            "fan_speed": data[56],
            "fan_flags": data[57],
        }

    def _decode_fan_mode(self, fan_state: int, fan_flags: int) -> FanMode | None:
        """Decode the fan mode."""
        if fan_flags & 0x40 == 0:
            return FanMode.ANTI_ALLERGY

        return self.FAN_STATE_TO_MODE.get(fan_state, FanMode.UNKNOWN)

    def _send(
        self,
        operation: int,
        action: int = 0,
        action_arg: int = 0,
    ) -> bytes:
        """Send a LIFAair command."""
        packet = bytearray(26)
        packet[0x02] = 0xA5
        packet[0x03] = 0xA5
        packet[0x04] = 0x5A
        packet[0x05] = 0x5A
        packet[0x08] = operation & 0xFF
        packet[0x0A] = 0x0C
        packet[0x0E] = action & 0xFF
        packet[0x0F] = action_arg & 0xFF

        checksum = sum(packet, 0xBEAF) & 0xFFFF
        packet[0x06] = checksum & 0xFF
        packet[0x07] = checksum >> 8

        packet_len = len(packet) - 2
        packet[0x00] = packet_len & 0xFF
        packet[0x01] = packet_len >> 8

        response = self.send_packet(0x6A, packet)
        broadlink_exceptions.check_error(response[0x22:0x24])
        return self.decrypt(response[0x38:])
