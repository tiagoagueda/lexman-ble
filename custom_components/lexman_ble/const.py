"""Constants for Lexman BLE integration."""

NAME = "LexmanBLE"
DOMAIN = "lexman_ble"

DEVICE_TIMEOUT = 30

# Vendor-specific GATT service the bulb advertises. Used to identify the device
# during manual config-flow discovery; mirrors the manifest.json bluetooth matcher.
SERVICE_UUID = "0000a100-1115-1000-0001-617573746f6d"

UPDATE_SECONDS = 15
