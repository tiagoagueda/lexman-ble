"""Constants for Lexman BLE integration."""

NAME = "LexmanBLE"
DOMAIN = "lexman_ble"

DEVICE_TIMEOUT = 30

# Vendor-specific GATT service that the CCT bulbs advertise. Used to identify the
# device during manual config-flow discovery; mirrors the manifest.json bluetooth
# matcher (which pairs it with manufacturer_id 5393).
#
# Do NOT relax the matcher to manufacturer_id 5393 alone: other Lexman/Adeo BLE
# products share that manufacturer id but speak a different protocol this
# integration cannot drive (one such sibling was observed advertising the same
# manufacturer id with manufacturer-data type byte 0x04 instead of the bulbs'
# 0x02, and without this custom 128-bit UUID). Requiring this UUID keeps discovery
# scoped to the CCT bulbs.
SERVICE_UUID = "0000a100-1115-1000-0001-617573746f6d"

UPDATE_SECONDS = 15
