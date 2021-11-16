# Bluesky Hardware Proxy

This is a proxy server to provide access to certain bluesky device methods over a zmq interface.
The interface is based directly on the zmq interface of bluesky-queueserver, so an identical client (with a different address) can be used.
For convenience, a version of `zmq_single_request` with the default address of `tcp://localhost:60620` is provided as `bluesky_hwproxy.comms.zmq_single_request`.

## Starting a server

`start-hwproxy-server` is an entry point provided to start up an instance of hwproxy.
It accepts the same parameters for specifying the environment that contains device objects as `start-re-manager` from bluesky-queueserver.

for example:

```bash
$ start-hwproxy-server --startup-script ./startup.py
$ start-hwproxy-server --startup-module ophyd.sim
$ start-hwproxy-server --startup-dir ./startup/
```

Note that at present, `--startup-profile` is not connected, though will be in the near future.

## Connecting via python

```python
from bluesky_hwproxy.comms import zmq_single_request

devices = zmq_single_request("list")[0]["result"]

describe = zmq_single_request("describe", {"device":devices[-1]})[0]["result"]
```

## Connecting via cli

We provide a `hwproxy` command line program to allow interfacing with the hwproxy server

Commands to interact with the server itself:
```bash
$ hwproxy list # List available hardware as string keys, one per line
motor1
motor2
det

$ hwproxy reload # reload available devices
```

The following print JSON response to the terminal:

```bash
$ hwproxy read <device>
$ hwproxy describe <device>
$ hwproxy config read <device>
$ hwproxy config describe <device>
$ hwproxy hints <device>
```

Output is colorized when run from an interactive shell, plain text when e.g. piped.

Finally, we allow checking if a set position is valid:
```bash
$ hwproxy check <device> <value>
true
```

The result is simply `true` or `false` printed to the terminal.

`<value>` can be any json encoded string (most of the time it is a simple float, however pseudopositioners and specialized hardware may use lists, etfc.
