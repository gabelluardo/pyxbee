# pylint: disable=unused-wildcard-import
from ..base import *

import pytest
import json
import random


# class TestPacket:
#     def test_one(self):
#         pass


# Questo test deve essere eseguito con
# l'antenna NON collegata al pc
class TestServerNotConnected:
    def setup(self):
        self.srv = Server()
        self.srv.listener = Taurus('0', 'listener0', self.srv)

    def test_device(self):
        assert self.srv.device is None

    def test_address(self):
        assert self.srv.address == 'None'

    def test_listener(self):
        server = Server()
        assert server.listener == {}

        tau0 = Taurus('0', 'listener0', server)
        tau1 = Taurus('1', 'listener1', server)

        server.listener = tau0
        server.listener = tau1
        assert server.listener == {'0': tau0, '1': tau1}

    def test_manage_packet(self):
        dest = self.srv.listener.get('0')
        test_packet = {
            '0': {
                'dest': '0',
                'type': '0',
                'heartrate': str(random.random()),
                'power': str(random.random()),
                'cadence': str(random.random()),
                'distance': str(random.random()),
                'speed': str(random.random()),
                'time': str(random.random()),
                'gear': str(random.random())
            },
            '1': {
                'dest': '0',
                'type': '1',
                'log': True,
                'video': True,
                'ant': False,
                'video_running': True,
                'video_recording': True,
                'powermeter_running': False,
                'heartrate_running': True,
                'speed_running': False,
                'calibration': True
            },
            '2': {
                'dest': '0',
                'type': '2',
                'valore': ''
            },
            '3': {
                'dest': '0',
                'type': '3',
                'circonferenza': str(random.random()),
                'run': str(random.random()),
                'log': False,
                'csv': False,
                'ant': False,
                'potenza': str(random.random()),
                'led': str(random.random()),
                'calibration_value': str(random.random()),
                'update': 'dsfasdfasdfasdf',
                'p13': True
            },
            '4': {
                'dest': '4',
                'type': '',
                'valore': ''
            },
            '5': {
                'dest': '',
                'type': '5',
                'messaggio': '',
                'priorita': '',
                'durata': '',
                'timeout': ''
            },
            '6': {
                'dest': '',
                'type': '6',
                'valore': ''
            },
            '7': {
                'dest': '',
                'type': '7',
                'value': '',
                'name_file': ''
            }
        }
        data = test_packet[Packet.Type.DATA]
        packet = Packet(data)
        self.srv.manage_packet(packet)
        assert dest.data == packet.jsonify

        state = test_packet[Packet.Type.STATE]
        packet = Packet(state)
        self.srv.manage_packet(packet)
        assert dest.state == packet.jsonify

        setting = test_packet[Packet.Type.SETTING]
        packet = Packet(setting)
        self.srv.manage_packet(packet)
        assert dest.setting == packet.jsonify

        # TODO: Inserire gli altri pacchetti

# class TestClient:
#     def test_one(self):
#         pass


# class TestBike:
#     def test_one(self):
#         pass


# class TestTaurus:
#     def test_one(self):
#         pass
