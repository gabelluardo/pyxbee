# Pyxbee

![Status](https://img.shields.io/badge/status-beta-yellow.svg)
[![Version](https://img.shields.io/pypi/v/pyxbee)](https://pypi.python.org/pypi/pyxbee/)
[![License](https://img.shields.io/github/license/gabelluardo/pyxbee?color=blue)](https://github.com/gabelluardo/pyxbee/blob/master/LICENSE)
[![Python Version](https://img.shields.io/pypi/pyversions/pyxbee)](https://www.python.org/downloads/)

Modulo di comunicazione per [Marta](https://github.com/gabelluardo/marta)

Fornisce classi di alto livello per interfacciarsi col modulo [digi-xbee](https://github.com/digidotcom/xbee-python) e le antenne xbee


## Installazione

    pip install pyxbee

oppure clonando il repository:

    git clone https://github.com/gabelluardo/pyxbee
    cd pyxbee/
    python3 setup.py install

## License

LGPLv3


***


### Legenda (da aggiornare)

#### CAMPI PACCHETT0

    0.  "destinatario"    0 -> Taurus | 1 -> TaurusX  
    1.  "tipo"            0 >> 7
    2.  "contenuto"       varia in base al tipo di pacchetto

#### TIPO DI PACCHETTO

Vedi [il protocollo](https://github.com/gabelluardo/pyxbee/issues/24)

    0  -> DATI
    1  -> STATE
    2  -> NOTIFICA
    3  -> IMPOSTAZIONI
    4  -> SEGNALI
    5  -> MESSAGGI
    6  -> GESTIONE RASPBERRY
    7  -> VIDEO

SEGNALI:

    0  -> calibra cambio
    1  -> calibra powermeter
    2  -> reset
    ...
    13 -> p13
    ...

RASPBERRY:

    0  -> spengi
    1  -> riavvia
    ...

VIDEO:

    0  -> avvio video
    1  -> termina video e salva

#### PORTA USB

    dmesg | grep tty

#### INDIRIZZI ANTENNE

    arduino nano v2 (cavo giallo) -> "0013A200418AF52F"
    ardiuno nano v1 (due cavi)    -> "0013A200418AE5A9"
    arduino uno                   -> "0013A200418AE577"
