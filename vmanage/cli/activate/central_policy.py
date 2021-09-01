import click
from vmanage.api.central_policy import CentralPolicy
from vmanage.api.utilities import Utilities


@click.command('central-policy')
@click.option('--name', '-n', help="Name of policy to activate.")
@click.pass_obj
def central_policy(ctx, name):
    """
    Activate Central Policy
    """

    vmanage_central_policy = CentralPolicy(ctx.auth, ctx.host, ctx.port)
    vmanage_utilities = Utilities(ctx.auth, ctx.host, ctx.port)
    central_policy_dict = vmanage_central_policy.get_central_policy_dict(remove_key=True)
    if name in central_policy_dict:
        click.echo(f'Activating Central Policy {name}')
        action_id = vmanage_central_policy.activate_central_policy(name, central_policy_dict[name]['policyId'])
        vmanage_utilities.waitfor_action_completion(action_id)
    else:
        click.secho(f'Cannot find Central Policy {name}', fg="red")
