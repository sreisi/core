"""The cover entity of reisinger intellidrive."""

import logging
from typing import Any, cast

from homeassistant.components.cover import (
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_TOKEN
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import ReisingerCoordinator
from .entity import IntelliDriveEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Intellidrive covers."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            SlidingDoorCoverEntity(
                hass,
                coordinator,
                str(entry.data.get(CONF_HOST)),
                str(entry.data.get(CONF_TOKEN)),
                cast(str, entry.unique_id),
            )
        ]
    )


class SlidingDoorCoverEntity(IntelliDriveEntity, CoverEntity):
    """Wrapper class to adapt the intellidrive device into the Homeassistant platform."""

    def __init__(
        self,
        hass: HomeAssistant,
        coordinator: ReisingerCoordinator,
        host: str,
        token: str,
        device_id: str,
    ) -> None:
        """Initialize slidingdoor cover."""
        super().__init__(coordinator, device_id)
        self._state: str | None = None
        self._state_before_move: str | None = None
        self._host = host
        self._token = token
        self._device_api = coordinator.device
        # self._attr_device_class = CoverDeviceClass.GARAGE

    async def async_close_cover(self, **kwargs: Any) -> None:
        """Close the door async."""
        await self._device_api.async_close()

    async def async_open_cover(self, **kwargs: Any) -> None:
        """Open the door async."""
        await self._device_api.async_open()

    async def async_stop_cover(self, **kwargs: Any) -> None:
        """Stop the door async."""
        await self._device_api.async_stop_door()

    def stop_cover(self, **kwargs: Any) -> None:
        """Stop the door."""
        self.hass.async_add_executor_job(self.async_stop_cover, **kwargs)

    def open_cover(self, **kwargs: Any) -> None:
        """Open the door."""
        self.hass.async_add_executor_job(self.async_open_cover, **kwargs)

    def close_cover(self, **kwargs: Any) -> None:
        """Close the door."""
        self.hass.async_add_executor_job(self.async_close_cover, **kwargs)

    @property
    def device_class(self) -> CoverDeviceClass:
        """Return the class of this device."""
        return CoverDeviceClass.DOOR

    @property
    def supported_features(self) -> CoverEntityFeature:
        """Flag supported features."""
        return (
            CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE | CoverEntityFeature.STOP
        )

    @callback
    def _update_attr(self) -> None:
        """Update the state and attributes."""
        status = self.coordinator.data

        self._attr_name = f"Slidingdoor {status['serial']}"
        # self._attr_name = "Name des Gerätes"

        # state = STATES_MAP.get(status.get("door"))  # type: ignore[arg-type]
        # if self._state_before_move is not None:
        #     if self._state_before_move != state:
        #         self._state = state
        #         self._state_before_move = None
        # else:
        #     self._state = state

    @property
    def is_closed(self) -> bool:
        """Get state if the door is closed."""

        open_status = self._device_api.get_is_open()
        return not open_status

    @property
    def is_closing(self) -> bool:
        """Get state if the door is closing now."""
        closing_status = self._device_api.get_is_closing()
        # Not supported yet
        return closing_status

    @property
    def is_opening(self) -> bool:
        """Get state if the door is opening now."""
        opening_status = self._device_api.get_is_opening()

        # Not supported yet
        return opening_status
