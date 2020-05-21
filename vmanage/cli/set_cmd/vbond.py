import click
from vmanage.api.settings import Settings


@click.command()
@click.option('--ip', 'ip', help="IP address of the vBond", required=True)
@click.option('--port', 'port', help="Port of the vBond", default='12346', required=False)
@click.pass_obj
def vbond(ctx, ip, port):
    """
    Set vBond
    """

    vmanage_settings = Settings(ctx.auth, ctx.host)
    vmanage_settings.set_vmanage_vbond(ip, port)
