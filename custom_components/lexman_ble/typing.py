"""Type aliases for the Lexman BLE integration."""

from homeassistant.config_entries import ConfigEntry

from .models import LexmanCCTSmartBulbData

type LexmanConfigEntry = ConfigEntry[LexmanCCTSmartBulbData]
