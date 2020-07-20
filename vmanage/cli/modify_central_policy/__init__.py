import click
from vmanage.cli.modify_central_policy.modify_approute_policy import modify_approute_policy

@click.group()
def modify_central_policy():
    """
    modify central policy commands
    """

modify_central_policy.add_command(modify_approute_policy)
