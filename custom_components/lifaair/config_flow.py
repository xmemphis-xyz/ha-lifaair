"""Config flow for LIFAair."""

from __future__ import annotations

import logging
from typing import Any

import broadlink
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import callback

from .const import DEVTYPE_LIFAAIR, DOMAIN

_LOGGER = logging.getLogger(__name__)


class LifaAirConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a LIFAair config flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()

            try:
                device = await self.hass.async_add_executor_job(
                    broadlink.hello,
                    host,
                )

                if device.devtype != DEVTYPE_LIFAAIR:
                    errors["base"] = "not_lifaair"
                else:
                    await self.hass.async_add_executor_job(device.auth)
                    await self.async_set_unique_id(
                        ":".join(f"{byte:02x}" for byte in device.mac)
                    )
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=device.name or "LIFAair",
                        data={CONF_HOST: host},
                    )
            except Exception as err:
                _LOGGER.debug(
                    "Unable to connect to LIFAair at %s: %s",
                    host,
                    err,
                )
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return no options flow."""
        return None
