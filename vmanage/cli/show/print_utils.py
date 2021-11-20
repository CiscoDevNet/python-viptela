import json

import click


def print_json(obj: dict):
    """
    Print a dictionary object as json
    """
    click.echo(json.dumps(obj, indent=2))
