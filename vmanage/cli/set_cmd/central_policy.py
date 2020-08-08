import click
from vmanage.api.policy_updates import PolicyUpdates


@click.command('central-policy')
@click.option('--type', '-t', help="Policy Type (supported option is approute)", required=True)
@click.option('--name', '-n', help="Policy name", required=True)
@click.option('--pref-color', '-prefcolor', help="Preferred color", required=True)
@click.option('--seq-name', '-seqname', help="Approute policy sequence name", required=False, default=None)
@click.pass_obj
def central_policy(ctx, type, name, pref_color, seq_name):
    """
    Change policy statements
    """

    vmanage_policy_updates = PolicyUpdates(ctx.auth, ctx.host)
    policy_id = vmanage_policy_updates.get_policy_id(type, name)
    policy_def = vmanage_policy_updates.get_policy_definition(type, policy_id)
    vmanage_policy_updates.update_policy_definition(type, name, policy_id, policy_def, pref_color, seq_name)
