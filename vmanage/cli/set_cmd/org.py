import click
from vmanage.api.settings import Settings


@click.command()
@click.argument('org_name', nargs=1)
@click.pass_obj
def org(ctx, org_name):
    """
    Set vManage org
    """

    vmanage_settings = Settings(ctx.auth, ctx.host, ctx.port)
    vmanage_settings.set_vmanage_org(org_name)
