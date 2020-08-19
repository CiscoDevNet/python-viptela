import click
from vmanage.api.certificate import Certificate


@click.command('root-cert')
@click.pass_obj
def root_cert(ctx):
    """
    Get vManage root certificate
    """

    vmanage_certificate = Certificate(ctx.auth, ctx.host, ctx.port)
    result = vmanage_certificate.get_vmanage_root_cert()
    click.echo(result)
