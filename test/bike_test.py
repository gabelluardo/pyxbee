import json
import pytest

# pylint: disable=wildcard-import,unused-wildcard-import
from pyxbee.exception import *
from pyxbee import Client, Bike, Packet

from test import test_packet


class TestBike:
    def setup(self):
        self.client = Client()
        self.bike = Bike('X', 'serverX', self.client)

    def test_init(self):
        c1 = Client()
        bike0 = Bike('0', 'server0', c1)

        bike1 = Bike('1', 'server0')

        bike2 = Bike('2', 'server2')

        with pytest.raises(InvalidInstanceException):
            Bike('0', 'server0', self.client)

        with pytest.raises(InvalidInstanceException):
            Bike('3', 'server3', self.client)

        assert bike0.code == '0'
        assert bike1.code == '1'
        assert bike0.address == 'server0'
        assert bike2.address == 'server2'

        assert self.bike.transmitter is self.client
        assert self.client.bike is self.bike
        assert self.bike.sensors is None

    def test_send(self):
        with pytest.raises(PacketInstanceException):
            self.bike.blind_send(list())

        with pytest.raises(InvalidInstanceException):
            self.bike.send_data(list())

        with pytest.raises(InvalidInstanceException):
            self.bike.send_state(list())

        with pytest.raises(InvalidInstanceException):
            self.bike.send_setting(list())

    def test_receive(self):
        list_ = list()
        with pytest.raises(PacketInstanceException):
            self.bike.receive(dict())

        with pytest.raises(PacketInstanceException):
            self.bike.receive(str())

        setting = dict(test_packet[Packet.Type.SETTING])
        packet = Packet(setting)
        self.bike.receive(packet)
        list_.append(packet)

        signal = dict(test_packet[Packet.Type.SIGNAL])
        packet = Packet(signal)
        self.bike.receive(packet)
        list_.append(packet)

        message = dict(test_packet[Packet.Type.MESSAGE])
        packet = Packet(message)
        self.bike.receive(packet)
        list_.append(packet)

        raspberry = dict(test_packet[Packet.Type.RASPBERRY])
        packet = Packet(raspberry)
        self.bike.receive(packet)
        list_.append(packet)

        video = dict(test_packet[Packet.Type.VIDEO])
        packet = Packet(video)
        self.bike.receive(packet)
        list_.append(packet)

        assert list(self.bike.packets) == list_

    def test_secret_key(self):
        key = b"test"

        c = Client()
        _ = Bike('Y', 'serverY', c, secret_key=key)
        p = Packet()

        assert p.secret_key == key
