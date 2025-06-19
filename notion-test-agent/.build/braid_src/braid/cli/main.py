import click
import os

from braid.cli.commands.new import new_command
from braid.cli.commands.package import package_command
from braid.cli.commands.add_pro_pack import add_pro_pack_command

@click.group()
def cli():
    """Braid Agent Builder CLI"""
    pass

cli.add_command(new_command, name="new")
cli.add_command(package_command, name="package")
cli.add_command(add_pro_pack_command, name="add-pro-pack")

if __name__ == "__main__":
    cli() 