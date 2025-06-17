import click
import os

from braid.cli.commands.new import new_command

@click.group()
def cli():
    """Braid Agent Builder CLI"""
    pass

cli.add_command(new_command, name="new")

if __name__ == "__main__":
    cli() 