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
@parse_output
def list():
    return zmq_single_request("list")

@main.command()
@parse_output
def reload():
    return zmq_single_request("reload")

@main.command()
@device_arg
@parse_output
def read(device):
    return zmq_single_request("read", {"device": device})

@main.command()
@device_arg
@parse_output
def describe(device):
    return zmq_single_request("describe", {"device": device})

@main.group()
def config():
    pass

@config.command()
@device_arg
@parse_output
def read(device):
    return zmq_single_request("read_configuration", {"device": device})

@config.command()
@device_arg
@parse_output
def describe(device):
    return zmq_single_request("describe_configuration", {"device": device})

@main.command()
@device_arg
@parse_output
def hints(device):
    return zmq_single_request("hints", {"device": device})

@main.command()
@device_arg
@click.argument("value")
@parse_output
def check(device, value):
    value = json.loads(value)
    return zmq_single_request("check_value", {"device": device, "value": value})

if __name__ == "__main__":
    main()

