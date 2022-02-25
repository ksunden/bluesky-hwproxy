import functools
from collections.abc import Sequence
import json

import click
import rich

from .comms import zmq_single_request

device_arg = click.argument("device", nargs=1)

def parse_output(fn):
    @functools.wraps(fn)
    def inner(*args, **kwargs):
        ret, err_msg = fn(*args, **kwargs)
        if err_msg:
            raise click.UsageError(err_msg)
        if not ret.get("success", False):
            raise click.UsageError(ret.get("msg"))
        if "return" in ret:
            ret = ret["return"]
        if isinstance(ret, Sequence):
            for r in ret:
                rich.print(r)
        elif ret is not None:
            rich.print_json(data=ret)
    return inner


@click.group()
@click.help_option()
@click.version_option()
@click.option("--address", default="tcp://localhost:60620")
def main(address):
    pass

@main.command()
@click.argument("protocol", type=str, required=False)
@parse_output
def list(protocol=None):
    """List available devices."""
    return zmq_single_request("list", {"protocol": protocol})

@main.command()
@parse_output
def reload():
    """Reload the available devices using the source as defined by the server."""
    return zmq_single_request("reload")

@main.command()
@device_arg
@parse_output
def read(device):
    """Read fields of a device."""
    return zmq_single_request("read", {"device": device})

@main.command()
@device_arg
@parse_output
def describe(device):
    """Describe metadata about the fields of a device."""
    return zmq_single_request("describe", {"device": device})

@main.group()
def config():
    """Provide read/describe for configuration of a device."""
    pass

@config.command()
@device_arg
@parse_output
def read(device):
    """Read configuration fields of a device."""
    return zmq_single_request("read_configuration", {"device": device})

@config.command()
@device_arg
@parse_output
def describe(device):
    """Describe metadata about configuration fields of a device."""
    return zmq_single_request("describe_configuration", {"device": device})

@main.command()
@device_arg
@parse_output
def hints(device):
    """Provide hints for a device which may be useful for visualization and processing."""
    return zmq_single_request("hints", {"device": device})

@main.command()
@device_arg
@parse_output
def component_names(device):
    """Provide component_names for a device which may be useful for visualization and processing."""
    return zmq_single_request("component_names", {"device": device})

@main.command()
@device_arg
@click.argument("value")
@parse_output
def check(device, value):
    """Test for valid setpoint without actually moving."""
    value = json.loads(value)
    return zmq_single_request("check_value", {"device": device, "value": value})

if __name__ == "__main__":
    main()

