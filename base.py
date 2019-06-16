import json
import logging

from digi.xbee.devices import RemoteXBeeDevice, XBeeDevice
from digi.xbee.exception import (InvalidOperatingModeException,
                                 InvalidPacketException, TimeoutException)
from digi.xbee.models.address import XBee64BitAddress
from serial.serialutil import SerialException

log = logging.getLogger(__name__)

PORT = "/dev/ttyUSB0"
BAUD_RATE = 115200

# NOTE: ogni nuovo pacchetto
# che deve essere mandato al
# frontend deve avere la sua costante
class Const:
    @property
    def DATA(self):
        return '0'

    @property
    def STATE(self):
        return '1'


# questa classe si interfaccia in con
# le funzioni di basso livello
# dello xbee e si occupa i mandare
# e ricevere raw_message formati da
# stringhe del tipo {};{};{};{}
class _Transmitter:
    def __init__(self):
        self.device = self.__open_device(PORT, BAUD_RATE)

    # DIREZIONE: server --> bici
    def send(self, address, packet):
        try:
            self.device.send_data_async(RemoteXBeeDevice(
                self.device, XBee64BitAddress.from_hex_string(address)), packet.encode)
        except (TimeoutException, InvalidPacketException):
            log.error('Dispositivo ({}) non trovato\n'.format(address))

    def send_sync(self, address, packet):
        # aspetta l'ack, se scatta il
        # timeout e non riceve risposta
        # lancia l'eccezione
        try:
            self.device.send_data(RemoteXBeeDevice(
                self.device, XBee64BitAddress.from_hex_string(address)), packet.encode)
        except (TimeoutException, InvalidPacketException):
            log.error('ACK send_sync non ricevuto\n')

    def send_broadcast(self, packet):
        self.device.send_data_broadcast(packet.encode)

    # DIREZIONE: bici --> server
    def receiver(self, xbee_message):
        # Viene richiamato nelle classi figlio
        pass

    def __open_device(self, port, baud_rate):
        device = XBeeDevice(port, baud_rate)
        try:
            device.open()
            device.add_data_received_callback(self.receiver)
            log.info('Antenna ({}) collegata\n'.format(device.get_64bit_addr()))
            return device
        except (InvalidOperatingModeException, SerialException):
            log.error('Nessuna antenna trovata')

    def __del__(self):
        if self.device is not None and self.device.is_open():
            log.debug('Device ({}) close'.format(self.device.get_64bit_addr()))
            self.device.close()


# SERVER mode del transmitter
class Server(_Transmitter):
    def __init__(self):
        super().__init__()
        self.__listener = dict()

    @property
    def listener(self):
        return self.__listener

    @listener.setter
    def listener(self, l):
        self.__listener.update({l.code: l})

    # DIREZIONE: bici --> server
    def receiver(self, xbee_message):
        # per gestire il pacchetto vuoto
        if xbee_message != '':
            raw = xbee_message.data.decode()
            packet = Packet(raw)
            log.debug('Received packet: {}'.format(packet))
            dest = self.listener.get(packet.content[0])
            dest.receive(packet)


# CLIENT mode del transmitter
class Client(_Transmitter):
    def __init__(self):
        super().__init__()

    def receiver(self, xbee_message):
        # quando riceve un pacchetto
        # dal server aggiorna i valori
        # nelle opportune classi della bici
        pass


# questa classe crea dei pacchetti
# contenitori sottoforma di liste
# e fornisce metodi per facilitare la
# comunicazione con il frontend
class Packet:
    def __init__(self, content=tuple()):
        self.__content = self.__decode(content)

    @property
    def content(self):
        return self.__content

    @content.setter
    def content(self, content):
        self.__content = self.__decode(content)

    @property
    def encode(self):
        return ';'.join(map(str, self.content))

    @property
    def jsonify(self):
        tipo = self.content[1]
        content = list(self.content[:])
        content.reverse()

        with open('pyxbee/packets.json') as f:
            res = json.load(f)[str(tipo)]

        for key, _ in res.items():
            res[key] = content.pop()
        return json.dumps(res)

    @classmethod
    def __decode(cls, data):
        # se viene passato un dict, una lista o una
        # stringa cruda la trasforma in tupla
        if isinstance(data, (list, tuple)):
            res = data
        elif isinstance(data, dict):
            res = [i for i in data.values()]
        else:
            res = data.split(';')
        return tuple(res)

    def __len__(self):
        return len(self.content)

    def __str__(self):
        return str(self.content)


# questa classe instazia l'antenna
# della bici corrispondente e conserva
# i dati trasmetti sottoforma di Packet,
# si occupa anche dell'invio di
# pacchetti verso l'antenna server
#
# id --> codice con cui viene identif. nei pacchetti
# address --> indirizzo dell'antenna
# transmitter --> instanza dell'antenna server
class Taurus:
    def __init__(self, code, address, server):
        self.address = address
        self.code = code
        self.transmitter = server

        # inserisce l'istanza corrente
        # nei listener dell'antenna del server
        self.transmitter.listener = self

        # Constanti per il dizionario dei pacchetti
        self.CONST = Const()

        # memorizza i dati sottoforma
        # di pacchetti ricevuti
        self.__memoize = dict()

        # colleziona i pacchetti mandati al frontend
        # per visualizzarli al reload della pagina con
        # soluzione di continuita'
        self.__history = list()

    @property
    def data(self):
        data = self.__memoize.get(self.CONST.DATA)
        jdata = data.jsonify if data != None else {}
        self.__history.append(jdata)
        return jdata

    @property
    def state(self):
        state = self.__memoize.get(self.CONST.STATE)
        return state.jsonify if state != None else {}

    @property
    def history(self):
        return self.__history

    # TODO: Inserire gli altri pacchetti

    # DIREZIONE: server --> bici
    def send(self, packet):
        self.transmitter.send(self.address, Packet(packet))

    def receive(self, packet):
        tipo = packet.content[1]
        self.__memoize.update({tipo: packet})

    def __str__(self):
        return self.code + ' -- ' + self.address
