import json
import pytest

# pylint: disable=wildcard-import,unused-wildcard-import
from pyxbee.exception import *
from pyxbee import Client, Packet, Bike

from test import test_packet


class TestClient:
    """
    Questo test puo' essere eseguito
    con l'antenna NON collegata
    """

    def test_init(self):
        Client()

        c1 = Client('ciao', 100)
        assert c1.port == 'ciao' and c1.baud_rate == 100

        c2 = Client(port='ciao', baud_rate=100)
        assert c2.port == 'ciao' and c2.baud_rate == 100

        with pytest.raises(ValueError):
            Client('a', 'b')

        with pytest.raises(ValueError):
            Client(100, 100)

        with pytest.raises(ValueError):
            Client(100, 'ciao')

    def test_parent(self):
        c = Client()
        assert c.device is None
        assert c.address == 'None'

    def test_bike(self):
        client = Client()
        assert client.bike is None

        bike0 = Bike('0', 'server0', client)
        assert client.bike == bike0

        with pytest.raises(InvalidInstanceException):
            Bike('1', 'server1', client)

        with pytest.raises(InvalidInstanceException):
            client.bike = bike0

        with pytest.raises(InvalidInstanceException):
            client.bike = dict()

        with pytest.raises(InvalidInstanceException):
            client.bike = list()

    def test_manage_packet(self):
        client = Client()
        bike = Bike('0', 'bike0', client)

        with pytest.raises(PacketInstanceException):
            client.manage_packet(dict())

        with pytest.raises(PacketInstanceException):
            client.manage_packet(str())

        data = dict(test_packet[Packet.Type.DATA])
        packet1 = Packet(data)
        client.manage_packet(packet1)

        state = dict(test_packet[Packet.Type.STATE])
        packet2 = Packet(state)
        client.manage_packet(packet2)

        setting = dict(test_packet[Packet.Type.SETTING])
        packet3 = Packet(setting)
        client.manage_packet(packet3)

        assert len(bike) == 3
        assert bike.packets == {packet1, packet2, packet3}
