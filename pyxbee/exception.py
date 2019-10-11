class PyxbeeException(Exception):
    pass


class InvalidTypeException(PyxbeeException):

    __DEFAULT_MESSAGE = "Packet type out of range (0-7)"

    def __init__(self, _message=__DEFAULT_MESSAGE):
        PyxbeeException.__init__(self, _message)


class InvalidFieldsException(PyxbeeException):

    __DEFAULT_MESSAGE = "The packet has few or too mach fields"

    def __init__(self, _message=__DEFAULT_MESSAGE):
        PyxbeeException.__init__(self, _message)


class InvalidInstanceExeption(PyxbeeException):

    __DEFAULT_MESSAGE = ""

    def __init__(self, _message=__DEFAULT_MESSAGE):
        PyxbeeException.__init__(self, _message)


class PacketInstanceExecption(PyxbeeException):

    __DEFAULT_MESSAGE = "This accepts only Packet instances"

    def __init__(self, _message=__DEFAULT_MESSAGE):
        PyxbeeException.__init__(self, _message)
