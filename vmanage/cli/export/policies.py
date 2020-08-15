import click
from vmanage.apps.files import Files


@click.command()
# @click.argument(policy_type, default='all')
@click.option('--file', '-f', 'export_file', help="output File name", required=True)
# @click.option('--type',
#               help="Device type [vedges, controllers]",
#               type=click.Choice(['vedges', 'controllers']))
@click.pass_obj
def policies(ctx, export_file):
    """
    Export policies to file
    """

    vmanage_files = Files(ctx.auth, ctx.host, ctx.port)
    click.echo(f'Exporting policies to {export_file}')
    vmanage_files.export_policy_to_file(export_file)
