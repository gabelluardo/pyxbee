# pylint: disable=wildcard-import,unused-wildcard-import,attribute-defined-outside-init

import pytest
import json
import random

from pyxbee import *
from pyxbee.exception import *

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
        'log': bool(random.randint(0, 1)),
        'video': bool(random.randint(0, 1)),
        'ant': bool(random.randint(0, 1)),
        'video_running': bool(random.randint(0, 1)),
        'video_recording': bool(random.randint(0, 1)),
        'powermeter_running': bool(random.randint(0, 1)),
        'heartrate_running': bool(random.randint(0, 1)),
        'speed_running': bool(random.randint(0, 1)),
        'calibration': bool(random.randint(0, 1))
    },
    '2': {
        'dest': '0',
        'type': '2',
        'valore': str(random.randint(0, 7))
    },
    '3': {
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
    },
    '4': {
        'dest': '0',
        'type': '4',
        'valore': str(random.randint(0, 13))
    },
    '5': {
        'dest': '0',
        'type': '5',
        'messaggio': str(random.random()),
        'priorita': str(random.randint(0, 5)),
        'durata': str(random.random()),
        'timeout': str(random.random())
    },
    '6': {
        'dest': '0',
        'type': '6',
        'valore': str(random.randint(0, 1))
    },
    '7': {
        'dest': '0',
        'type': '7',
        'value': bool(random.randint(0, 1)),
        'name_file': str(random.random())
    }
}


class TestPacket:
    def test_load(self):
        for tipo in test_packet.keys():
            tester = dict(test_packet[tipo])
            tester_tuple = tuple([tester[val] for val in tester.keys()])
            tester_list = list(tester_tuple)
            tester_str = ';'.join(map(str, tester.values()))

            # load con dizionario
            p1 = Packet(tester)

            assert p1.jsonify == json.dumps(tester)
            assert p1.dictify == tester
            assert p1.content == tester_tuple
            assert len(p1) == len(tester)
            assert str(p1) == str(tuple(tester.values()))

            # per la comparazione di due packetti uguali
            p2 = Packet(tester)

            assert p1.jsonify == p2.jsonify
            assert p1.dictify == p2.dictify
            assert p1.content == p2.content
            assert p1.value == p2.value
            assert p1.encode == p2.encode

            # load con tupla
            p3 = Packet(tester_tuple)

            assert p1.jsonify == p3.jsonify
            assert p1.dictify == p3.dictify
            assert p1.content == p3.content
            assert p1.value == p3.value
            assert p1.encode == p3.encode

            # load con lista
            p4 = Packet(tester_list)

            assert p1.jsonify == p4.jsonify
            assert p1.dictify == p4.dictify
            assert p1.content == p4.content
            assert p1.value == p4.value
            assert p1.encode == p4.encode

            # load con stringa
            p5 = Packet(tester_str)

            assert p1.content == p5.content
            assert p1.value == p5.value
            assert p1.encode == p5.encode
            assert p1.jsonify == p5.jsonify
            assert p1.dictify == p5.dictify

    def test_wrong_type(self):
        values = ['19', '-1', 'a', '=', ';', '', ',', 'é']

        for char in values:
            with pytest.raises(InvalidTypeException):
                Packet('0;'+char)

    def test_fields_packet(self):
        with pytest.raises(InvalidFieldsException):
            Packet({'dest': '0', 'type': '0'})

        tester = dict(test_packet[Packet.Type.DATA])
        tester.pop('gear')
        with pytest.raises(InvalidFieldsException):
            Packet(tester)

    def test_content(self):
        tester = dict(test_packet[Packet.Type.DATA])
        p1 = Packet(tester)

        assert p1.content == tuple(tester.values())

        tester2 = dict(test_packet[Packet.Type.DATA])
        tester2['gear'] = 11
        p2 = Packet(tester2)

        assert p1.content != p2.content
        assert p1.value != p2.value
        assert len(p1) == len(p2)

        tester2['dest'] = 2
        p3 = Packet(tester2)

        assert p2.content != p3.content
        assert p2.value == p3.value
        assert len(p2) == len(p3)


class TestServerNotPlugged:
    # Questo test deve essere eseguito
    # con l'antenna NON collegata
    def setup(self):
        self.srv = Server()
        self.srv.listener = Taurus('0', 'listener0', self.srv)

    def test_init(self):
        Server()
        Server('ciao', 100)

        with pytest.raises(ValueError):
            Server('a', 'b')

        with pytest.raises(ValueError):
            Server(100, 100)

        with pytest.raises(ValueError):
            Server(100, 'ciao')

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

        data = dict(test_packet[Packet.Type.DATA])
        packet = Packet(data)
        self.srv.manage_packet(packet)
        assert dest.data == packet.jsonify

        state = dict(test_packet[Packet.Type.STATE])
        packet = Packet(state)
        self.srv.manage_packet(packet)
        assert dest.state == packet.jsonify

        setting = dict(test_packet[Packet.Type.SETTING])
        packet = Packet(setting)
        self.srv.manage_packet(packet)
        assert dest.setting == packet.jsonify

        # TODO: Inserire gli altri pacchetti


class TestClientNotPlugged:
    # Questo test deve essere eseguito
    # con l'antenna NON collegata
    pass


class TestServer:
    # @TODO: Aggiungere test classe Server (antenna collegata)
    # Questo test deve essere eseguito
    # con l'antenna collegata
    pass


class TestClient:
    # @TODO: Aggiungere test classe Client (antenna collegata)
    # Questo test deve essere eseguito
    # con l'antenna collegata
    pass


class TestBike:
    # @TODO: Aggiungere test classe Bike (antenna collegata)
    # Questo test deve essere eseguito
    # con l'antenna collegata
    pass


class TestTaurus:
    # @TODO: Aggiungere test classe Taurus (antenna collegata)
    # Questo test deve essere eseguito
    # con l'antenna collegata
    pass
