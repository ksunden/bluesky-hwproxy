import functools

from bluesky_queueserver.manager.comms import zmq_single_request, ZMQCommSendThreads

zmq_single_request = functools.partial(zmq_single_request, zmq_server_address="tcp://localhost:60620")

class ZMQCommSendThreads(ZMQCommSendThreads):
    def __init__(
        self,
        *,
        zmq_server_address=None,
        timeout_recv=2000,
        timeout_send=500,
        raise_exceptions=True,
        server_public_key=None,
    ):
        super().__init__(
            zmq_server_address=zmq_server_address or "tcp://localhost:60620",
            timeout_recv=timeout_recv,
            timeout_send=timeout_send,
            raise_exceptions=raise_exceptions,
            server_public_key=server_public_key,
        )

