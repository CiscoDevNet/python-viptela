import click
from vmanage.api.certificate import Certificate


@click.command('install')
@click.option('--cert', '-c', help="Certificate to install.")
@click.pass_obj
def install(ctx, cert):
    """
    Install certificate
    """

    vmanage_certificate = Certificate(ctx.auth, ctx.host)
    click.echo("Installing certificate...")
    vmanage_certificate.install_device_cert(cert)