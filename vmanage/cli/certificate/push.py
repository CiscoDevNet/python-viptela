import click
from vmanage.api.certificate import Certificate


@click.command()
@click.pass_obj
def push(ctx):
    """
    Push certificates to all controllers
    """

    vmanage_certificate = Certificate(ctx.auth, ctx.host, ctx.port)
    click.echo("Pushing certificates to controllers...")
    vmanage_certificate.push_certificates()
