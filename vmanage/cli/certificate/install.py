import click
from vmanage.api.certificate import Certificate


@click.command('install')
@click.option('--file', '-f', help="File containing the certificate to install.", required=True)
@click.pass_obj
def install(ctx, cert):
    """
    Install certificate
    """

    vmanage_certificate = Certificate(ctx.auth, ctx.host, ctx.port)
    click.echo("Installing certificate...")
    vmanage_certificate.install_device_cert(cert)
