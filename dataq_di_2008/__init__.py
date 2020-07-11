
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

from .usb_bulk_driver import Driver
from .device import Device
