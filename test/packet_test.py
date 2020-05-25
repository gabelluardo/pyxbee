import json
import pytest

from hashlib import blake2s

# pylint: disable=wildcard-import,unused-wildcard-import
from pyxbee.exception import *
from pyxbee import Packet

from test import test_packet, json_path


class TestPacket:
    def setup(self):
        Packet.secret_key = None

    def test_load(self):
        for tipo in test_packet.keys():
            tester = dict(test_packet[tipo])
            tester_tuple = tuple([tester[val] for val in tester.keys()])
            tester_list = list(tester_tuple)
            tester_str = ';'.join(map(str, tester.values()))

            # load con dizionario
            p1 = Packet(tester)
            print(p1)
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
        with open(json_path) as p:
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

    def test_digest(self):
        Packet.secret_key = b"test_key"
        protected_type = Packet().protected_type

        for tipo in protected_type:
            tester = dict(test_packet[tipo])

            p1 = Packet(tester)
            p2 = Packet(tester)

            assert p1.secret_key == p2.secret_key

            assert p1.content == p2.content
            assert p1.value == p2.value
            assert p1.encode == p2.encode
            assert p1.jsonify == p2.jsonify
            assert p1.dictify == p2.dictify
            assert p1.digest == p2.digest

        for tipo in protected_type:
            tester = dict(test_packet[tipo])

            Packet.secret_key = b"test_key"
            p1 = Packet(tester)

            assert p1.secret_key == b"test_key"

            Packet.secret_key = b"test_key2"
            p2 = Packet(tester)

            assert p2.secret_key == b"test_key2"

            # aggiornando la secret_key si aggiorna per tutti
            assert p1.secret_key == p2.secret_key

            assert p1.content != p2.content
            assert p1.value != p2.value
            assert p1.encode != p2.encode
            assert p1.jsonify != p2.jsonify
            assert p1.dictify != p2.dictify
            assert p1.digest != p2.digest

    def test_hashing(self):
        Packet.secret_key = b"test_key"
        protected_type = Packet().protected_type

        for tipo in protected_type:
            tester = dict(test_packet[tipo])

            p = Packet(tester)

            h = blake2s(key=Packet.secret_key, digest_size=16)
            h.update(json.dumps(p.raw_data).encode('utf-8'))

            assert p.digest == h.hexdigest()
