import json
import logging

from abc import ABC

from .const import PROTOCOL
from .exception import InvalidTypeException, InvalidFieldsException

log = logging.getLogger(__name__)


class _ABCPacket(ABC):

    _PACKETS = dict(PROTOCOL)

    # tipi pacchetto per il protocollo standard
    class Type:
        DATA = '0'
        STATE = '1'
        NOTICE = '2'
        SETTING = '3'
        SIGNAL = '4'
        MESSAGE = '5'
        RASPBERRY = '6'
        VIDEO = '7'

    def __init__(self, content=None):
        if content is None:
            content = tuple()
        self._content = self._decode(content)

    @property
    def content(self):
        return self._content

    @classmethod
    def protocol(cls, protocol=None):
        """Metodo per inserire un protocollo custom"""
        if isinstance(protocol, dict):
            cls._PACKETS = dict(protocol)
        elif isinstance(protocol, str):
            cls._PACKETS = dict(json.loads(protocol))
        else:
            cls._PACKETS = dict(PROTOCOL)

        return cls._PACKETS

    def _decode(self, data):
        """Se viene passato un dizionario aggiorna
        i valori da un pacchetto corrispondente vuoto;
        se viene passata una lista/tupla/stringa
        ne estrae i valori e li salva in tupla.
        """
        self._check_data(data)

        # ORDINE VALORI NON IMPORTANTE
        if isinstance(data, dict):
            d = dict(self._PACKETS[str(data['type'])])
            d.update(data)
            res = d.values()
        # ORDINE VALORI IMPORTANTE
        elif isinstance(data, (list, tuple)):
            res = data
        else:
            res = [json.loads(item.lower()) if item.lower() in ['true', 'false']
                   else item for item in data.split(';')]

        return tuple(res)

    def _check_data(self, data):
        if isinstance(data, dict):
            content = data.values()
            tipo = data['type']
        else:
            content = data if isinstance(data, (list, tuple)) else data.split(';')
            tipo = content[1]

        # check valid type
        if tipo not in self._PACKETS.keys():
            raise InvalidTypeException

        # check valid len
        if len(content) != len(self._PACKETS[tipo].values()):
            raise InvalidFieldsException

    def __len__(self):
        return len(self._content)

    def __str__(self):
        return str(self._content)


class Packet(_ABCPacket):
    """
    Questa classe crea dei pacchetti
    contenitori sottoforma di tuple
    e fornisce metodi per facilitare la
    comunicazione con il frontend e gli xbee
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
