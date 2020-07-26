import click
from vmanage.api.policy_updates import PolicyUpdates


@click.command('modify-approute-policy')
@click.option('--name', '-n', help="Approute policy name", required=True)
@click.option('--pref-color', '-prefcolor', help="Preferred color", required=True)
@click.option('--seq-name', '-seqname', help="Approute policy sequence name", required=False, default=None)
@click.pass_obj
def modify_approute_policy(ctx, name, pref_color, seq_name):
    """
    Change app route policy
    """

    vmanage_policy_updates = PolicyUpdates(ctx.auth, ctx.host)
    policy_id = vmanage_policy_updates.get_policy_id("approute", name)
    policy_def = vmanage_policy_updates.get_policy_definition("approute", policy_id)
    vmanage_policy_updates.update_policy_definition("approute", name, policy_id, policy_def, pref_color, seq_name)
