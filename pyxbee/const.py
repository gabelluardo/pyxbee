PORT = '/dev/ttyUSB0'
BAUD_RATE = 115200

PROTOCOL = {
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
