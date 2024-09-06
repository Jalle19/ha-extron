"""Config flow for Extron integration."""

import logging

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.helpers.selector import selector

from .const import CONF_DEVICE_TYPE, CONF_HOST, CONF_PASSWORD, CONF_PORT, DOMAIN
from .extron import AuthenticationError, DeviceType, ExtronDevice

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=23): int,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_DEVICE_TYPE): selector(
            {
                "select": {
                    "options": [
                        {"label": "HDMI Switcher", "value": DeviceType.HDMI_SWITCHER.value},
                        {"label": "Surround Sound Processor", "value": DeviceType.SURROUND_SOUND_PROCESSOR.value},
                    ]
                }
            }
        ),
    }
)


class ExtronConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Extron."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                # Try to connect to the device
                extron_device = ExtronDevice(user_input["host"], user_input["port"], user_input["password"])
                await extron_device.connect()

                # Make a title for the entry
                model_name = await extron_device.query_model_name()
                title = f"Extron {model_name}"

                # Disconnect, we'll connect again later, this was just for validation
                await extron_device.disconnect()
            except AuthenticationError:
                errors["base"] = "invalid_auth"
            except Exception:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title=title, data=user_input)

        return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors)
