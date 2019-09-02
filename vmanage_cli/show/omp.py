import click
import pprint

@click.command()
@click.option('--device_ip', default='', help="Show information for device")
@click.option('--json/--no-json', default=False)
@click.option('--type', default='all',
               help="Device type [vedges, controllers]",
               type=click.Choice(['vedges', 'controllers', 'all']))
@click.pass_context
def summary(ctx, device_ip, type, json):
    """
    Show device information
    """

    vmanage_session = ctx.obj
    click.echo("omp summary")

@click.group()
@click.pass_context
def omp(ctx):
    """
    OMP commands
    """

omp.add_command(summary)

