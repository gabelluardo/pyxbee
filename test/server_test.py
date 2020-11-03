import json
import pytest

# pylint: disable=wildcard-import,unused-wildcard-import
from pyxbee.exception import *
from pyxbee import Server, Taurus, Packet

from test import test_packet


class TestServer:
    """
    Questo test puo' essere eseguito
    con l'antenna NON collegata
    """

    def test_init(self):
        Server()

        s1 = Server('ciao', 100)
        assert s1.port == 'ciao' and s1.baud_rate == 100

        s2 = Server(port='ciao', baud_rate=100)
        assert s2.port == 'ciao' and s2.baud_rate == 100

        with pytest.raises(ValueError):
            Server('a', 'b')

        with pytest.raises(ValueError):
            Server(100, 100)

        with pytest.raises(ValueError):
            Server(100, 'ciao')

    def test_parent(self):
        s = Server()
        assert s.device is None
        assert s.address == 'None'

    def test_listener(self):
        server = Server()
        assert server.listener == dict()

        tau0 = Taurus('0', 'listener0', server=server)
        tau1 = Taurus('1', 'listener1', server=server)

        assert server.listener == {'0': tau0, '1': tau1}

        with pytest.raises(InvalidInstanceException):
            server.listener = dict()

        with pytest.raises(InvalidInstanceException):
            server.listener = list()

    def test_manage_packet(self):
        server = Server()
        dest = Taurus('X', 'listenerX', server=server)

        with pytest.raises(PacketInstanceException):
            server.manage_packet(dict())

        with pytest.raises(PacketInstanceException):
            server.manage_packet(str())

        data = dict(test_packet[Packet.Type.DATA])
        packet = Packet(data)
        server.manage_packet(packet)
        assert dest.data == packet.jsonify

        state = dict(test_packet[Packet.Type.STATE])
        packet = Packet(state)
        server.manage_packet(packet)
        assert dest.state == packet.jsonify

        setting = dict(test_packet[Packet.Type.SETTING])
        packet = Packet(setting)
        server.manage_packet(packet)
        assert dest.setting == packet.jsonify

        # TODO: Inserire gli altri pacchetti
