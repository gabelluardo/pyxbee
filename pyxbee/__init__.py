import re

from .base import Bike, Client, Server, Taurus
from .const import PROTOCOL
from .packet import Packet
from .exception import *


with open('pyproject.toml', 'r') as f:
    __version__ = re.search(r'^version\s*=\s*[\'"]([^\'"]*)[\'"]',
                            f.read(), re.MULTILINE).group(1)


__all__ = [
    'Bike',
    'Client',
    'Server',
    'Taurus',
    'Packet',
    'base',
    'packet',
    'exception',
    'PROTOCOL'
]
