import click
from vmanage.api.policy_updates import PolicyUpdates


@click.command('central-policy')
@click.option('--type', '-t', 'type_', help="Policy Type (supported option is approute)", required=True)
@click.option('--name', '-n', help="Policy name", required=True)
@click.option('--pref-color', help="Preferred color", required=True)
@click.option('--seq-name', help="Approute policy sequence name", required=False, default=None)
@click.pass_obj
def central_policy(ctx, type_, name, pref_color, seq_name):
    """
    Set Policy sequence statements
    """

    vmanage_policy_updates = PolicyUpdates(ctx.auth, ctx.host, ctx.port)
    policy_id = vmanage_policy_updates.get_policy_id(type_, name)
    policy_def = vmanage_policy_updates.get_policy_definition(type_, policy_id)
    vmanage_policy_updates.update_policy_definition(type_, name, policy_id, policy_def, pref_color, seq_name)
