import click
from vmanage.api.settings import Settings


@click.command('ca-type')
@click.option('--type', 'type_', required=True, type=click.Choice(['enterprise'], case_sensitive=False))
@click.pass_obj
def ca_type(ctx, type_):
    """
    Set vManage CA type
    """

    vmanage_settings = Settings(ctx.auth, ctx.host, ctx.port)
    vmanage_settings.set_vmanage_ca_type(type_)
