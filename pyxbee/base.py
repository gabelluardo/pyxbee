import logging

from abc import ABC, abstractmethod

from digi.xbee.devices import RemoteXBeeDevice, XBeeDevice
from digi.xbee.exception import (InvalidOperatingModeException,
                                 InvalidPacketException, TimeoutException)
from digi.xbee.models.address import XBee64BitAddress
from serial.serialutil import SerialException
from ordered_set import OrderedSet

from .const import PORT, BAUD_RATE
from .packet import Packet
from .exception import (InvalidInstanceException, PacketInstanceException,
                        InvalidCodeException, InvalidDigest)

log = logging.getLogger(__name__)


class _Transmitter(ABC):
    """
    Si interfaccia con la libreria
    dello xbee e si occupa i mandare
    e ricevere raw_message formati da
    stringhe del tipo `{};{};{};{}`

    I parametri dell'antenna xbee sono settati
    manualmente via software esterno  
    :param port: `str`
        Porta scelta per lo xbee
        DEFAULT: '/dev/ttyUSB0'
    :param baud_rate: `int`
        Baud rate scelto per lo xbee
        DEFAULT: `115200`
    """

    def __init__(self, port=PORT, baud_rate=BAUD_RATE):
        self._nonce = -1
        self._device = None

        self._port = port
        self._baud_rate = baud_rate

        self._open_device(port, baud_rate)

    def __del__(self):
        if self._device:
            if self._device.is_open():
                self._device.close()
                log.info(f'Device ({self._device.get_64bit_addr()}) closed')

    def _open_device(self, port, baud_rate):
        device = XBeeDevice(port, baud_rate)
        try:
            device.open()
            device.add_data_received_callback(self.receiver)
            log.info(f'Device ({device.get_64bit_addr()}) connected\n')
            self._device = device
        except (InvalidOperatingModeException, SerialException):
            log.error('Antenna not found')

    @property
    def device(self):
        return self._device

    @property
    def address(self):
        return self.device.get_64bit_addr() if self.device else 'None'

    @property
    def port(self):
        return self._port

    @property
    def baud_rate(self):
        return self._baud_rate

    # DIREZIONE: server --> bici

    def send(self, address, packet):
        try:
            self.device.send_data_async(RemoteXBeeDevice(
                self.device, XBee64BitAddress.from_hex_string(address)), packet.encode)
        except (TimeoutException, InvalidPacketException):
            log.error(f'({address}) not found\n')
        except AttributeError:
            log.error('SEND: Antenna not connected\n')

    def send_sync(self, address, packet):
        """Aspetta l'ack, se scatta il
        timeout e non riceve risposta
        lancia l'eccezione
        """
        try:
            self.device.send_data(RemoteXBeeDevice(
                self.device, XBee64BitAddress.from_hex_string(address)), packet.encode)
        except (TimeoutException, InvalidPacketException):
            log.error('ACK send_sync not received\n')
        except AttributeError:
            log.error('SEND_SYNC: Antenna not connected\n')

    def send_broadcast(self, packet):
        self.device.send_data_broadcast(packet.encode)

    # DIREZIONE: bici --> server

    def receiver(self, xbee_message):
        if xbee_message != '':
            raw = xbee_message.data.decode()
            packet = Packet(raw)
            log.debug(f'Received packet: {packet}')

            if packet.tipo in packet.protected_type:
                dig = packet.calculate_digest(packet.raw_data)
                nonce = int(packet.nonce)

                if dig == packet.digest and nonce > self._nonce:
                    self._nonce = nonce
                    self.manage_packet(packet)
                # TODO: vogliamo che venga laciata un'eccezione?
                # else:
                #     raise InvalidDigest
            else:
                self.manage_packet(packet)

    @abstractmethod
    def manage_packet(self, packet):
        pass


class _SuperBike(ABC):
    """Classe genitore per la modalita' server e client"""

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
        if not isinstance(packet, Packet):
            packet = Packet(packet)
        self.transmitter.send(self.address, packet)


class Server(_Transmitter):
    """SERVER mode del transmitter"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._listener = dict()

        self.web = None

    @property
    def listener(self):
        return self._listener

    @listener.setter
    def listener(self, l):
        if not isinstance(l, Taurus):
            raise InvalidInstanceException

        if l.code in self.listener.keys():
            raise InvalidCodeException

        self._listener.update({l.code: l})

    # DIREZIONE: bici --> server

    def manage_packet(self, packet):
        if not isinstance(packet, Packet):
            raise PacketInstanceException
        dest = self.listener.get(packet.dest)
        dest.receive(packet)

        if self.web and packet.tipo == Packet.Type.DATA:
            self.web.send_data(packet.encode)


class Taurus(_SuperBike):
    """
    Questa classe prende instaza dell'antenna in
    modalita' SERVER, conserva i pacchetti
    ricevuti in __memoize e si occupa
    dell'invio di pacchetti verso il CLIENT (bici)

    code --> codice con cui viene identif. nei pacchetti
    address --> indirizzo dell'antenna client
    server --> instanza dell'antenna server
    """

    def __init__(self, code, address, xbee_port=PORT, server=None, secret_key=None):
        if not server:
            server = Server(port=xbee_port)

        if secret_key:
            Packet.secret_key = secret_key

        super().__init__(code, address, server)

        # inserisce l'istanza corrente
        # nei listener dell'antenna del server
        self.transmitter.listener = self

        # colleziona i pacchetti mandati al frontend
        # per visualizzarli al reload della pagina con
        # soluzione di continuita'
        self._history = OrderedSet()

        # memorizza un pacchetto
        # ricevuto per ogni tipo
        self._memoize = dict()

    def __str__(self):
        return f'{self.code} -- {self.address}'

    @property
    def history(self):
        return list(self._history)

    @property
    def data(self):
        data = self._memoize.get(Packet.Type.DATA)
        if data:
            self._history.append(data.jsonify)
        return data.jsonify if data else {}

    @property
    def state(self):
        state = self._memoize.get(Packet.Type.STATE)
        return state.jsonify if state else {}

    @property
    def setting(self):
        sett = self._memoize.get(Packet.Type.SETTING)
        return sett.jsonify if sett else {}

    @property
    def notice(self):
        notice = self._memoize.get(Packet.Type.NOTICE)
        return notice.jsonify if notice else {}

    # DIREZIONE: bici --> server

    def receive(self, packet):
        if not isinstance(packet, Packet):
            raise PacketInstanceException
        self._memoize.update({packet.tipo: packet})


class Client(_Transmitter):
    """CLIENT mode del transmitter"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bike = None

    @property
    def bike(self):
        return self._bike

    @bike.setter
    def bike(self, b):
        if not isinstance(b, Bike):
            raise InvalidInstanceException
        if self._bike is not None:
            raise InvalidInstanceException
        self._bike = b

    # DIREZIONE: server --> bici

    def manage_packet(self, packet):
        if not isinstance(packet, Packet):
            raise PacketInstanceException
        self.bike.receive(packet)


class Bike(_SuperBike):
    """
    Questa classe prende instaza dell'antenna in
    modalita' CLIENT, conserva i pacchetti
    ricevuti in __memoize e si occupa
    dell'invio di pacchetti verso il SERVER (marta)

    code --> codice con cui viene identif. nei pacchetti
    address --> indirizzo dell'antenna server
    client --> instanza dell'antenna client
    """

    def __init__(self, code, address, client=None, sensors=None, secret_key=None):
        if not client:
            client = Client()

        if secret_key:
            Packet.secret_key = secret_key

        super().__init__(code, address, client)

        # memorizza le instanze dei valori utili
        self._sensors = sensors

        # inserisce l'instanza corrente
        # come client dell'antenna
        self.transmitter.bike = self

        # memorizza tutti i pacchetti ricevuti
        self._memoize = OrderedSet()

    def __len__(self):
        return len(self._memoize)

    def __str__(self):
        return f'{self.code} -- {self.transmitter.address}'

    @property
    def packets(self):
        return self._memoize

    @property
    def sensors(self):
        return self._sensors

    # DIREZIONE: bici -> server

    def blind_send(self, packet):
        if not isinstance(packet, Packet):
            raise PacketInstanceException
        self.send(packet)

    def send_data(self, d):
        if not isinstance(d, dict):
            raise InvalidInstanceException

        data = {'dest': self.code, 'type': Packet.Type.DATA}
        data.update(d)
        self.send(data)

    # NOTE: probabilmente da deprecare
    def send_state(self, s):
        if not isinstance(s, dict):
            raise InvalidInstanceException

        state = {'dest': self.code, 'type': Packet.Type.STATE}
        state.update(s)
        self.send(state)

    def send_setting(self, s):
        if not isinstance(s, dict):
            raise InvalidInstanceException

        settings = {'dest': self.code, 'type': Packet.Type.SETTING}
        settings.update(s)
        self.send(settings)

    # TODO: Aggiungere pacchetto NOTICE

    # DIREZIONE: server --> bici

    def receive(self, packet):
        if not isinstance(packet, Packet):
            raise PacketInstanceException
        self._memoize.append(packet)
