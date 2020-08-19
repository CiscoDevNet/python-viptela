import click
from vmanage.apps.files import Files


@click.command()
@click.option('--file', '-f', 'export_file', help="Output file name", required=True)
@click.option('--name', '-n', multiple=True)
@click.option('--type',
              '-t',
              'template_type',
              help="Template type",
              type=click.Choice(['device', 'feature']),
              default=None)
@click.pass_obj
def templates(ctx, template_type, name, export_file):
    """
    Export templates to file
    """
    vmanage_files = Files(ctx.auth, ctx.host, ctx.port)

    if template_type == 'device':
        if name:
            click.echo(f'Exporting device template(s) {",".join(name)} to {export_file}')
            vmanage_files.export_templates_to_file(export_file, name_list=name, template_type='device')
        else:
            click.echo(f'Exporting device templates to {export_file}')
            vmanage_files.export_templates_to_file(export_file, template_type='device')
    elif template_type == 'feature':
        if name:
            click.echo(f'Exporting feature template(s) {",".join(name)} to {export_file}')
            vmanage_files.export_templates_to_file(export_file, name_list=name, template_type='feature')
        else:
            click.echo(f'Exporting feature templates to {export_file}')
            vmanage_files.export_templates_to_file(export_file, template_type='feature')
    else:
        if name:
            raise click.ClickException("Must specify template type with name")
        click.echo(f'Exporting templates to {export_file}')
        vmanage_files.export_templates_to_file(export_file)
