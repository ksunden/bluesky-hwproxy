import functools

from bluesky_queueserver.manager.comms import zmq_single_request

zmq_single_request = functools.partial(zmq_single_request, zmq_server_address="tcp://localhost:60620")
