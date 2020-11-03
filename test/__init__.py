import random

json_path = 'test/assets/packets.json'

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
