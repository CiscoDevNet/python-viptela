import click
from vmanage.api.settings import Settings


@click.command('vbond')
@click.pass_obj
def vbond(ctx):
    """
    Get IP address and port for the configured vBond
    """

    vmanage_settings = Settings(ctx.auth, ctx.host, ctx.port)
    result = vmanage_settings.get_vmanage_vbond()
    if 'domainIp' in result:
        click.echo('{}:{}'.format(result['domainIp'], result['port']))
    else:
        click.echo("No vBond configured")
