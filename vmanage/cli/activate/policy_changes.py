import click
from vmanage.api.policy_updates import PolicyUpdates


@click.command('policy-changes')
@click.option('--policy_type', '-policytype', help="Type of policy")
@click.option('--name', '-n', help="Policy name")
@click.option('--pref_color', '-prefcolor', help="Preferred color" )
@click.pass_obj
def policy_changes(ctx, policy_type, name, pref_color):
    """
    Change app route policy
    """

    vmanage_policy_updates = PolicyUpdates(ctx.auth, ctx.host)
    policy_id = vmanage_policy_updates.get_policy_id(policy_type,name)
    policy_def = vmanage_policy_updates.get_policy_definition(policy_type,policy_id)

    vmanage_policy_updates.update_policy_definition(policy_type, policy_id, policy_def, pref_color)

    click.echo(f'Updated app route policy {name}')