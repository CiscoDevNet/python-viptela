import click
from vmanage.api.settings import Settings


@click.command('org')
@click.pass_obj
def org(ctx):
    """
    Get vManage org
    """

    vmanage_settings = Settings(ctx.auth, ctx.host, ctx.port)
    result = vmanage_settings.get_vmanage_org()
    if result:
        click.echo(f'{result}')
    else:
        click.echo("No org configured")
