import json
import logging

from digi.xbee.devices import RemoteXBeeDevice, XBeeDevice
from digi.xbee.exception import (InvalidOperatingModeException,
                                 InvalidPacketException, TimeoutException)
from digi.xbee.models.address import XBee64BitAddress
from serial.serialutil import SerialException
from abc import abstractmethod

from pyxbee.exception import InvalidTypeException

log = logging.getLogger(__name__)

PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200

PACKETS = {
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
    '2': {
        'dest': '',
        'type': '2',
        'valore': ''
    },
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


# questa classe si interfaccia in con
# le funzioni di basso livello
# dello xbee e si occupa i mandare
# e ricevere raw_message formati da
# stringhe del tipo {};{};{};{}
class _Transmitter:
    def __init__(self):
        self._device = None

        self._open_device(PORT, BAUD_RATE)

    def __del__(self):
        if self.device is not None:
            if self.device.is_open():
                self.device.close()
                log.debug('Device ({}) close'.format(self.device.get_64bit_addr()))

    def _open_device(self, port, baud_rate):
        device = XBeeDevice(port, baud_rate)
        try:
            device.open()
            device.add_data_received_callback(self.receiver)
            self._device = device
            log.info('Device ({}) connected\n'.format(device.get_64bit_addr()))
        except (InvalidOperatingModeException, SerialException):
            log.error('Nessuna antenna trovata')

    @property
    def device(self):
        return self._device

    @property
    def address(self):
        return self.device.get_64bit_addr() if self.device is not None else 'None'

    # DIREZIONE: server --> bici
    def send(self, address, packet):
        try:
            self.device.send_data_async(RemoteXBeeDevice(
                self.device, XBee64BitAddress.from_hex_string(address)), packet.encode)
        except (TimeoutException, InvalidPacketException):
            log.error('Dispositivo ({}) non trovato\n'.format(address))
        except AttributeError:
            log.error('SEND: Antenna non collegata\n')

    def send_sync(self, address, packet):
        # aspetta l'ack, se scatta il
        # timeout e non riceve risposta
        # lancia l'eccezione
        try:
            self.device.send_data(RemoteXBeeDevice(
                self.device, XBee64BitAddress.from_hex_string(address)), packet.encode)
        except (TimeoutException, InvalidPacketException):
            log.error('ACK send_sync non ricevuto\n')
        except AttributeError:
            log.error('SEND_SYNC: Antenna non collegata\n')

    def send_broadcast(self, packet):
        self.device.send_data_broadcast(packet.encode)

    # DIREZIONE: bici --> server
    def receiver(self, xbee_message):
        if xbee_message != '':
            raw = xbee_message.data.decode()
            packet = Packet(raw)
            log.debug('Received packet: {}'.format(packet))
            self.manage_packet(packet)

    @abstractmethod
    def manage_packet(self, packet):
        pass


# SERVER mode del transmitter
class Server(_Transmitter):
    def __init__(self):
        super().__init__()
        self._listener = dict()

        self.web = None

    @property
    def listener(self):
        return self._listener

    @listener.setter
    def listener(self, l):
        self._listener.update({l.code: l})

    # DIREZIONE: bici --> server
    def manage_packet(self, packet):
        dest = self.listener.get(packet.dest)
        dest.receive(packet)
        if self.web is not None and packet.tipo == Packet.Type.DATA:
            self.web.send_data(packet.encode)


# CLIENT mode del transmitter
class Client(_Transmitter):
    def __init__(self):
        super().__init__()
        self._bike = None

    @property
    def bike(self):
        return self._bike

    @bike.setter
    def bike(self, b):
        self._bike = b

    # DIREZIONE: server --> bici
    def manage_packet(self, packet):
        self.bike.receive(packet)


# questa classe crea dei pacchetti
# contenitori sottoforma di liste
# e fornisce metodi per facilitare la
# comunicazione con il frontend
class Packet:
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
    def __init__(self, content=tuple()):
        self._content = self._decode(content)

    def __len__(self):
        return len(self.content)

    def __str__(self):
        return str(self.content)

    @classmethod
    def _decode(cls, data):
        # se viene passato un dizionario aggiorna i
        # valori da un pacchetto vuoto.
        # ORDINE NON IMPORTANTE
        if isinstance(data, dict):
            if data['type'] not in PACKETS.keys():
                raise InvalidTypeException

            d = PACKETS[str(data['type'])]
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

        res = tuple(res)
        if res[1] not in PACKETS.keys():
            raise InvalidTypeException
        return res

    @property
    def content(self):
        return self._content

    # TODO: controllare se serve ancora
    @content.setter
    def content(self, content):
        self._content = self._decode(content)

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
        res = PACKETS[str(self.tipo)]

        for key, _ in res.items():
            res[key] = content.pop()
        return json.dumps(res)

    @property
    def dictify(self):
        return json.loads(self.jsonify)


# classe genitore per la modalita' server e client
class _SuperBike:
    def __init__(self, code, address, transmitter):
        self._address = address
        self._code = code
        self._transmitter = transmitter

    @property
    def transmitter(self):
        return self._transmitter

    @property
    def code(self):
        return self._code

    @property
    def address(self):
        return self._address

    @abstractmethod
    def receive(self, packet):
        pass

    # DIREZIONE: server --> bici
    def send(self, packet):
        data = packet if isinstance(packet, Packet) else Packet(packet)
        self.transmitter.send(self.address, data)


# questa classe prende instaza dell'antenna in
# modalita' CLIENT, conserva i pacchetti
# ricevuti in __memoize e si occupa
# dell'invio di pacchetti verso il SERVER (marta)
#
# code --> codice con cui viene identif. nei pacchetti
# address --> indirizzo dell'antenna server
# client --> instanza dell'antenna client
class Bike(_SuperBike):
    def __init__(self, code, address, client, sensors):
        super().__init__(code, address, client)

        # memorizza le instanze dei valori utili
        self._sensors = sensors

        # inserisce l'instanza corrente
        # come client dell'antenna
        self.transmitter.bike = self

        # memorizza i pacchetti ricevuti  (un pacchetto per tipo)
        self._memoize = list()

    def __len__(self):
        return len(self._memoize)

    def __str__(self):
        return '{} -- {}'.format(self.code, self.transmitter.address)

    @property
    def packets(self):
        return self._memoize

    # DIREZIONE: bici -> server
    def blind_send(self, packet: Packet):
        self.send(packet)

    def send_data(self, d: dict):
        data = {'dest': self.code, 'type': Packet.Type.DATA}
        data.update(d)
        self.send(data)

    # NOTE: probabilmente da deprecare
    def send_state(self, s: dict):
        state = {'dest': self.code, 'type': Packet.Type.STATE}
        state.update(s)
        self.send(state)

    def send_setting(self, s: dict):
        settings = {'dest': self.code, 'type': Packet.Type.SETTING}
        settings.update(s)
        self.send(settings)

    # TODO: Inserire gli altri pacchetti

    # DIREZIONE: server --> bici
    def receive(self, packet):
        self._memoize.append(packet)


# questa classe prende instaza dell'antenna in
# modalita' SERVER, conserva i pacchetti
# ricevuti in __memoize e si occupa
# dell'invio di pacchetti verso il CLIENT (bici)
#
# code --> codice con cui viene identif. nei pacchetti
# address --> indirizzo dell'antenna client
# server --> instanza dell'antenna server
class Taurus(_SuperBike):
    def __init__(self, code, address, server):
        super().__init__(code, address, server)

        # inserisce l'istanza corrente
        # nei listener dell'antenna del server
        self.transmitter.listener = self

        # colleziona i pacchetti mandati al frontend
        # per visualizzarli al reload della pagina con
        # soluzione di continuita'
        self._history = list()

        # memorizza un pacchetto
        # ricevuto per ogni tipo
        self._memoize = dict()

    def __str__(self):
        return '{} -- {}'.format(self.code, self.address)

    @property
    def history(self):
        return self._history

    @property
    def data(self):
        data = self._memoize.get(Packet.Type.DATA)
        jdata = data.jsonify if data is not None else {}
        self._history.append(jdata)
        return jdata

    @property
    def state(self):
        state = self._memoize.get(Packet.Type.STATE)
        return state.jsonify if state is not None else {}

    @property
    def setting(self):
        sett = self._memoize.get(Packet.Type.SETTING)
        return sett.jsonify if sett is not None else {}

    # TODO: Inserire gli altri pacchetti

    # DIREZIONE: bici --> server
    def receive(self, packet):
        self._memoize.update({packet.tipo: packet})
