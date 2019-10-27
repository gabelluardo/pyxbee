import json
import logging

from .exception import InvalidTypeException, InvalidFieldsException

log = logging.getLogger(__name__)

_PACKETS = {
    # DATA
    '0': {
        'dest': '',
        'type': '0',
        'heartrate': '',
        'power': '',
        'cadence': '',
        'distance': '',
        'speed': '',
        'time': '',
        'gear': ''
    },
    # STATE
    '1': {
        'dest': '',
        'type': '1',
        'log': '',
        'video': '',
        'ant': '',
        'video_running': '',
        'video_recording': '',
        'powermeter_running': '',
        'heartrate_running': '',
        'speed_running': '',
        'calibration': ''
    },
    # NOTICE
    '2': {
        'dest': '',
        'type': '2',
        'valore': ''
    },
    # SETTINGS
    '3': {
        'dest': '',
        'type': '3',
        'circonferenza': '',
        'run': '',
        'log': '',
        'csv': '',
        'ant': '',
        'potenza': '',
        'led': '',
        'calibration_value': '',
        'update': '',
        'p13': ''
    },
    # SIGNAL
    '4': {
        'dest': '',
        'type': '4',
        'valore': ''
    },
    # MESSAGE
    '5': {
        'dest': '',
        'type': '5',
        'messaggio': '',
        'priorita': '',
        'durata': '',
        'timeout': ''
    },
    # RASPBERRY
    '6': {
        'dest': '',
        'type': '6',
        'valore': ''
    },
    # VIDEO
    '7': {
        'dest': '',
        'type': '7',
        'value': '',
        'name_file': ''
    }
}


class Packet:
    """
    Questa classe crea dei pacchetti
    contenitori sottoforma di tuple
    e fornisce metodi per facilitare la
    comunicazione con il frontend e gli xbee
    """

    _PACKETS = dict(_PACKETS)

    class Type:
        DATA = '0'
        STATE = '1'
        NOTICE = '2'
        SETTING = '3'
        SIGNAL = '4'
        MESSAGE = '5'
        RASPBERRY = '6'
        VIDEO = '7'

    # @TODO: Passare ai dizionari
    def __init__(self, content=None, protocol=None):
        if content is None:
            content = tuple()
        self._content = self._decode(content)

    def __len__(self):
        return len(self.content)

    def __str__(self):
        return str(self.content)

    @classmethod
    def _decode(cls, data):
        cls._check_data(data)
        # se viene passato un dizionario aggiorna i
        # valori da un pacchetto vuoto.
        # ORDINE NON IMPORTANTE
        if isinstance(data, dict):
            d = dict(cls._PACKETS[str(data['type'])])
            d.update(data)
            res = d.values()
        # se viene passato un una lista/tupla/stringa
        # ne estrae i valori e li salva in tupla.
        # ORDINE IMPORTANTE
        elif isinstance(data, (list, tuple)):
            res = data
        else:
            res = [json.loads(item.lower()) if item.lower() in ['true', 'false']
                   else item for item in data.split(';')]

        return tuple(res)

    @classmethod
    def _check_data(cls, data):
        if isinstance(data, dict):
            content = data.values()
            tipo = data['type']
        else:
            content = data if isinstance(data, (list, tuple)) else data.split(';')
            tipo = content[1]

        # check valid type
        if tipo not in cls._PACKETS.keys():
            raise InvalidTypeException

        # check valid len
        if len(content) != len(cls._PACKETS[tipo].values()):
            raise InvalidFieldsException

    @classmethod
    def protocol(cls, protocol=None):
        """Metodo per inserire un protocollo"""
        if isinstance(protocol, dict):
            cls._PACKETS = dict(protocol)
        elif isinstance(protocol, str):
            cls._PACKETS = dict(json.loads(protocol))
        else:
            cls._PACKETS = dict(_PACKETS)

        return cls._PACKETS

    @property
    def content(self):
        return self._content

    @property
    def dest(self):
        return self.content[0] if len(self) > 0 else None

    @property
    def tipo(self):
        return self.content[1] if len(self) > 0 else None

    @property
    def value(self):
        return self.content[2:]

    @property
    def encode(self):
        return ';'.join(map(str, self.content))

    @property
    def jsonify(self):
        content = list(self.content[::-1])
        res = dict(self._PACKETS[str(self.tipo)])

        for key, _ in res.items():
            res[key] = content.pop()
        return json.dumps(res)

    @property
    def dictify(self):
        return json.loads(self.jsonify)
