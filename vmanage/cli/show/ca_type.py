import click
from vmanage.api.settings import Settings


@click.command('ca-type')
@click.pass_obj
def ca_type(ctx):
    """
    Get vManage CA type
    """

    vmanage_settings = Settings(ctx.auth, ctx.host, ctx.port)
    result = vmanage_settings.get_vmanage_ca_type()
    click.echo(result)
