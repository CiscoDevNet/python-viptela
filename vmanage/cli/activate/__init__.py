import click
from vmanage.cli.activate.central_policy import central_policy
from vmanage.cli.activate.policy_changes import policy_changes

@click.group()
def activate():
    """
    Activate commands
    """


activate.add_command(central_policy)
activate.add_command(policy_changes)
