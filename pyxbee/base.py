import logging

from digi.xbee.devices import RemoteXBeeDevice, XBeeDevice
from digi.xbee.exception import (InvalidOperatingModeException,
                                 InvalidPacketException, TimeoutException)
from digi.xbee.models.address import XBee64BitAddress
from serial.serialutil import SerialException
from abc import abstractmethod

from .packet import Packet

log = logging.getLogger(__name__)

PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200


# questa classe si interfaccia in con
# le funzioni di basso livello
# dello xbee e si occupa i mandare
# e ricevere raw_message formati da
# stringhe del tipo {};{};{};{}
class _Transmitter:
    def __init__(self, port, baud_rate):
        self._device = None

        self._open_device(port, baud_rate)

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
    def __init__(self, port=PORT, baud_rate=BAUD_RATE):
        super().__init__(port, baud_rate)
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
    def __init__(self, port=PORT, baud_rate=BAUD_RATE):
        super().__init__(port, baud_rate)
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
