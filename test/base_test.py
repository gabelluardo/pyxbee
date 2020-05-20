# pylint: disable=wildcard-import,unused-wildcard-import,attribute-defined-outside-init

import pytest
import json
import random

from pyxbee import *
from pyxbee.exception import *

test_packet = {
    # DATA
    '0': {
        'dest': 'X',
        'type': '0',
        'heartrate': str(random.random()),
        'power': str(random.random()),
        'cadence': str(random.random()),
        'distance': str(random.random()),
        'speed': str(random.random()),
        'time': str(random.random()),
        'gear': str(random.random())
    },
    # STATE
    '1': {
        'dest': 'X',
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
    # NOTICE
    '2': {
        'dest': 'X',
        'type': '2',
        'valore': str(random.randint(0, 7))
    },
    # SETTINGS
    '3': {
        'dest': 'X',
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
    # SIGNAL
    '4': {
        'dest': 'X',
        'type': '4',
        'valore': str(random.randint(0, 13))
    },
    # MESSAGE
    '5': {
        'dest': 'X',
        'type': '5',
        'messaggio': str(random.random()),
        'priorita': str(random.randint(0, 5)),
        'durata': str(random.random()),
        'timeout': str(random.random())
    },
    # RASPBERRY
    '6': {
        'dest': 'X',
        'type': '6',
        'valore': str(random.randint(0, 1))
    },
    # VIDEO
    '7': {
        'dest': 'X',
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
            assert str(p1) == str(tester)

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

    def test_protocol(self):
        with open('test/packets.json') as p:
            protocol = p.read()

        Packet.protocol(protocol)
        assert Packet._PACKETS == json.loads(protocol)

        protocol = {'primo': {'ciao': '', 'type': 'ciao'}}
        result = Packet.protocol(protocol)

        assert result == protocol
        assert Packet._PACKETS == protocol

        # reset protocollo
        result = Packet.protocol()
        assert result == Packet._PACKETS


class TestServer:
    # Questo test puo' essere eseguito
    # con l'antenna NON collegata
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


class TestClient:
    # Questo test puo' essere eseguito
    # con l'antenna NON collegata
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
