import asyncio
from typing import Optional

import click

from ._proxy import HardwareProxy


@click.command()
@click.help_option()
@click.version_option()
@click.option("--startup-script", default=None, type=click.Path(exists=True, dir_okay=False))
@click.option("--startup-module", default=None, type=str)
@click.option("--startup-profile", default=None, type=str)
@click.option("--startup-dir", default=None, type=click.Path(exists=True, file_okay=False))
@click.option("--zmq-addr", default="tcp://*:60620")
def main(startup_script, startup_module, startup_profile, startup_dir, zmq_addr):
    if sum((_ is not None for _ in (startup_script, startup_module, startup_profile, startup_dir))) != 1:
        raise click.UsageError("Please specify exactly one startup source.")
    hw_proxy = HardwareProxy(startup_script_path=startup_script, startup_module_name=startup_module, startup_dir=startup_dir)
    asyncio.run(hw_proxy.zmq_server_comm())

if __name__ == "__main__":
    main()

