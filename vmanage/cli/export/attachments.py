import click
from vmanage.apps.files import Files


@click.command()
@click.option('--type',
              '-t',
              'device_type',
              help="Device Type",
              type=click.Choice(['controllers', 'vedges']),
              default=None)
@click.option('--name', '-n', multiple=True)
@click.option('--file', '-f', 'output_file', help="Output file name", required=True)
@click.pass_obj
def attachments(ctx, device_type, name, output_file):
    """
    Export attachments to file
    """
    num = 0
    vmanage_files = Files(ctx.auth, ctx.host, ctx.port)
    if device_type == 'controllers':
        if name:
            click.echo(f'Exporting controller attachment(s) {",".join(name)} to {output_file}')
            num = vmanage_files.export_attachments_to_file(output_file, name_list=name, device_type=device_type)
        else:
            click.echo(f'Exporting controller attachment to {output_file}')
            num = vmanage_files.export_attachments_to_file(output_file, device_type=device_type)
    elif device_type == 'vedges':
        if name:
            click.echo(f'Exporting vedge attachment(s) {",".join(name)} to {output_file}')
            num = vmanage_files.export_attachments_to_file(output_file, name_list=name, device_type=device_type)
        else:
            click.echo(f'Exporting vedge attachment to {output_file}')
            num = vmanage_files.export_attachments_to_file(output_file, device_type=device_type)
    else:
        if name:
            click.echo(f'Exporting attachment(s) {",".join(name)} to {output_file}')
            num = vmanage_files.export_attachments_to_file(output_file, name_list=name, device_type=device_type)
        else:
            click.echo(f'Exporting attachment to {output_file}')
            num = vmanage_files.export_attachments_to_file(output_file, device_type=device_type)
    click.echo(f"Exported {num} attachments")
