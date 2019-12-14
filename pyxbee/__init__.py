import re

from .base import Bike, Client, Server, Taurus
from .packet import Packet
from .exception import *

__all__ = [
    'Bike',
    'Client',
    'Server',
    'Taurus',
    'Packet',
    'base',
    'packet',
    'exception'
]

with open('pyproject.toml', 'r') as f:
    __version__ = re.search(r'^version\s*=\s*[\'"]([^\'"]*)[\'"]',
                            f.read(), re.MULTILINE).group(1)
