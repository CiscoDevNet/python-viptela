import click
from vmanage.api.settings import Settings


@click.command('root-cert')
@click.option('--file', '-f', 'input_file', help="Certificate file name", required=True)
@click.pass_obj
def root_cert(ctx, input_file):
    """
    Import root cert
    """
    vmanage_settings = Settings(ctx.auth, ctx.host, ctx.port)
    vmanage_settings.set_vmanage_root_cert(input_file)
