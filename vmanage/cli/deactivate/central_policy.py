import click
from vmanage.api.central_policy import CentralPolicy


@click.command('central-policy')
@click.option('--name', '-n', help="Name of policy to deactivate.")
@click.option('--id', '-i', help="Id of policy to deactivate.")
@click.pass_obj
def central_policy(ctx, name, policy_id):
    """
    deactivate Central Policy
    """

    vmanage_central_policy = CentralPolicy(ctx.auth, ctx.host, ctx.port)
    central_policy_dict = vmanage_central_policy.get_central_policy_dict(remove_key=True)
    if policy_id:
        vmanage_central_policy.deactivate_central_policy(policy_id)
    elif name:
        if name in central_policy_dict:
            click.echo(f'Deactivating Central Policy {name}')
            action_id = vmanage_central_policy.deactivate_central_policy(central_policy_dict[name]['policyId'])
            vmanage_central_policy.waitfor_action_completion(action_id)
        else:
            click.secho(f'Cannot find Central Policy {name}', fg="red")
    else:
        click.secho('Must specify either policy name of id to deactivate', fg="red")
