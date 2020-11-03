import json
import pytest
import random

# pylint: disable=wildcard-import,unused-wildcard-import
from pyxbee.exception import *
from pyxbee import Server, Taurus, Packet

from test import test_packet


class TestTaurus:
    def setup(self):
        self.server = Server()
        self.taurus = Taurus('X', 'listenerX', '/dev/ttyUSB0', self.server)

    def test_init(self):
        tau0 = Taurus('0', 'listener0', server=self.server)
        tau1 = Taurus(code='1', address='listener1', xbee_port='/dev/ttyUSB0', server=self.server)

        assert tau0.code == '0'
        assert tau1.code == '1'
        assert tau0.address == 'listener0'
        assert tau1.address == 'listener1'

        tau2 = Taurus('2', 'listener2')

        assert tau2.code == '2'
        assert tau2.address == 'listener2'
        assert isinstance(tau2.transmitter, Server)
        assert tau2.transmitter.listener['2'] is tau2

        with pytest.raises(InvalidCodeException):
            Taurus('X', 'listenerX', server=self.server)

        assert tau0 in self.server.listener.values()
        assert tau1 in self.server.listener.values()

        assert self.taurus in self.server.listener.values()
        assert self.taurus.transmitter is self.server
        assert self.server.listener['X'] is self.taurus

    def test_data(self):
        tau0 = Taurus('0', 'listener0', server=self.server)
        tau1 = Taurus('1', 'listener1', server=self.server)

        assert tau0.data == {}
        assert tau1.data == {}

        packet1 = Packet({
            'dest': '0',
            'type': '0',
            'heartrate': str(random.random()),
            'power': str(random.random()),
            'cadence': str(random.random()),
            'distance': str(random.random()),
            'speed': str(random.random()),
            'time': str(random.random()),
            'gear': str(random.random())
        })
        self.server.manage_packet(packet1)

        assert tau0.data == packet1.jsonify
        assert tau1.data == {}

        packet2 = Packet({
            'dest': '1',
            'type': '0',
            'heartrate': str(random.random()),
            'power': str(random.random()),
            'cadence': str(random.random()),
            'distance': str(random.random()),
            'speed': str(random.random()),
            'time': str(random.random()),
            'gear': str(random.random())
        })
        self.server.manage_packet(packet2)

        assert tau0.data == packet1.jsonify
        assert tau1.data == packet2.jsonify

        packet3 = Packet({
            'dest': '1',
            'type': '0',
            'heartrate': str(random.random()),
            'power': str(random.random()),
            'cadence': str(random.random()),
            'distance': str(random.random()),
            'speed': str(random.random()),
            'time': str(random.random()),
            'gear': str(random.random())
        })
        self.server.manage_packet(packet3)

        assert tau0.data == packet1.jsonify
        assert tau1.data == packet3.jsonify

        # test per la funzione di history
        assert tau0.history == [packet1.jsonify]
        assert tau1.history == [packet2.jsonify, packet3.jsonify]

    def test_state(self):
        tau0 = Taurus('0', 'listener0', server=self.server)
        tau1 = Taurus('1', 'listener1', server=self.server)

        assert tau0.state == {}
        assert tau1.state == {}

        packet1 = Packet({
            'dest': '0',
            'type': '1',
            'log': bool(random.randint(0, 1)),
            'video': bool(random.randint(0, 1)),
            'ant': bool(random.randint(0, 1)),
            'video_running': bool(random.randint(0, 1)),
            'video_recording': bool(random.randint(0, 1)),
            'powermeter_running': bool(random.randint(0, 1)),
            'heartrate_running': bool(random.randint(0, 1)),
            'speed_running': bool(random.randint(0, 1)),
            'calibration': bool(random.randint(0, 1))
        })
        self.server.manage_packet(packet1)

        assert tau0.state == packet1.jsonify
        assert tau1.state == {}

        packet2 = Packet({
            'dest': '1',
            'type': '1',
            'log': bool(random.randint(0, 1)),
            'video': bool(random.randint(0, 1)),
            'ant': bool(random.randint(0, 1)),
            'video_running': bool(random.randint(0, 1)),
            'video_recording': bool(random.randint(0, 1)),
            'powermeter_running': bool(random.randint(0, 1)),
            'heartrate_running': bool(random.randint(0, 1)),
            'speed_running': bool(random.randint(0, 1)),
            'calibration': bool(random.randint(0, 1))
        })
        self.server.manage_packet(packet2)

        assert tau0.state == packet1.jsonify
        assert tau1.state == packet2.jsonify

        packet3 = Packet({
            'dest': '1',
            'type': '1',
            'log': bool(random.randint(0, 1)),
            'video': bool(random.randint(0, 1)),
            'ant': bool(random.randint(0, 1)),
            'video_running': bool(random.randint(0, 1)),
            'video_recording': bool(random.randint(0, 1)),
            'powermeter_running': bool(random.randint(0, 1)),
            'heartrate_running': bool(random.randint(0, 1)),
            'speed_running': bool(random.randint(0, 1)),
            'calibration': bool(random.randint(0, 1))
        })
        self.server.manage_packet(packet3)

        assert tau0.state == packet1.jsonify
        assert tau1.state == packet3.jsonify

    def test_setting(self):
        tau0 = Taurus('0', 'listener0', server=self.server)
        tau1 = Taurus('1', 'listener1', server=self.server)

        assert tau0.setting == {}
        assert tau1.setting == {}

        packet1 = Packet({
            'dest': '0',
            'type': '3',
            'circonferenza': str(random.random()),
            'run': str(random.random()),
            'log': bool(random.randint(0, 1)),
            'csv': bool(random.randint(0, 1)),
            'ant': bool(random.randint(0, 1)),
            'potenza': str(random.random()),
            'led': str(random.random()),
            'calibration_value': str(random.random()),
            'update': str(random.random()),
            'p13': bool(random.randint(0, 1))
        })
        self.server.manage_packet(packet1)

        assert tau0.setting == packet1.jsonify
        assert tau1.setting == {}

        packet2 = Packet({
            'dest': '1',
            'type': '3',
            'circonferenza': str(random.random()),
            'run': str(random.random()),
            'log': bool(random.randint(0, 1)),
            'csv': bool(random.randint(0, 1)),
            'ant': bool(random.randint(0, 1)),
            'potenza': str(random.random()),
            'led': str(random.random()),
            'calibration_value': str(random.random()),
            'update': str(random.random()),
            'p13': bool(random.randint(0, 1))
        })
        self.server.manage_packet(packet2)

        assert tau0.setting == packet1.jsonify
        assert tau1.setting == packet2.jsonify

        packet3 = Packet({
            'dest': '1',
            'type': '3',
            'circonferenza': str(random.random()),
            'run': str(random.random()),
            'log': bool(random.randint(0, 1)),
            'csv': bool(random.randint(0, 1)),
            'ant': bool(random.randint(0, 1)),
            'potenza': str(random.random()),
            'led': str(random.random()),
            'calibration_value': str(random.random()),
            'update': str(random.random()),
            'p13': bool(random.randint(0, 1))
        })
        self.server.manage_packet(packet3)

        assert tau0.setting == packet1.jsonify
        assert tau1.setting == packet3.jsonify

    def test_receive(self):
        with pytest.raises(PacketInstanceException):
            self.taurus.receive(dict())

        with pytest.raises(PacketInstanceException):
            self.taurus.receive(str())

        data = dict(test_packet[Packet.Type.DATA])
        packet = Packet(data)
        self.taurus.receive(packet)
        assert self.taurus.data == packet.jsonify

        state = dict(test_packet[Packet.Type.STATE])
        packet = Packet(state)
        self.taurus.receive(packet)
        assert self.taurus.state == packet.jsonify

        setting = dict(test_packet[Packet.Type.SETTING])
        packet = Packet(setting)
        self.taurus.receive(packet)
        assert self.taurus.setting == packet.jsonify

    def test_secret_key(self):
        key = b"test"

        _ = Taurus('X', 'listenerX', '/dev/ttyUSB0', secret_key=key)
        p = Packet()

        assert p.secret_key == key
