import functools

from .comms import ZMQCommSendThreads

def parse_output(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        ret = fn(*args, **kwargs)
        if not ret.get("success", False):
            raise ValueError(ret.get("msg"))
        return ret.get("return", None)
    return inner

class NullStatus:
    @property
    def done(self):
        return True

    @property
    def success(self):
        return True

    def add_callback(self, callback):
        callback(self)

class Device:
    def __init__(self, name, addr="tcp://localhost:60620"):
        self._name = name
        self._comm = ZMQCommSendThreads(zmq_server_address=addr)

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return None

    def trigger(self):
        return NullStatus()

    @parse_output
    def describe(self):
        return self._comm.send_message(method="describe", params={"device": self.name})

    @parse_output
    def read(self):
        return self._comm.send_message(method="read", params={"device": self.name})

    @parse_output
    def describe_configuration(self):
        return self._comm.send_message(method="describe_configuration", params={"device": self.name})

    @parse_output
    def read_configuration(self):
        return self._comm.send_message(method="read_configuration", params={"device": self.name})
