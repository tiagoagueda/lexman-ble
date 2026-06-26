"""Vendored Lexman CCT smart bulb BLE library.

Bundled into the integration (rather than installed from PyPI) so that local
changes ship directly via HACS. Originally the standalone `lexman-ble` package.
"""

from .cct_smart_bulb import BLEAK_EXCEPTIONS, LexmanCCTSmartBulb
from .models import LexmanCCTSmartBulbState

__all__ = ["BLEAK_EXCEPTIONS", "LexmanCCTSmartBulb", "LexmanCCTSmartBulbState"]
