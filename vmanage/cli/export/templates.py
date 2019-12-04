    
import click
import json

@click.command()
@click.option('--file', '-f', help="Output file name", required=True)
@click.option('--name', '-n', multiple=True)
@click.option('--type', '-t',
               help="Template type",
               type=click.Choice(['device', 'feature']),
               default=None)
@click.pass_context
def templates(ctx, type, name, file):
    """
    Export templates to file
    """
    vmanage_session = ctx.obj
    if type == 'device':
        if name:
            click.echo(f'Exporting device template(s) {",".join(name)} to {file}')
            vmanage_session.export_templates_to_file(file, name_list=name, type='device')
        else:
            click.echo(f'Exporting device templates to {file}')
            vmanage_session.export_templates_to_file(file, type='device')
    elif type == 'feature':
        if name:
            click.echo(f'Exporting feature template(s) {",".join(name)} to {file}')
            vmanage_session.export_templates_to_file(file, name_list=name, type_list='feature')
        else:
            click.echo(f'Exporting feature templates to {file}')
            vmanage_session.export_templates_to_file(file, type='feature')        
    else:
        if name:
            raise click.ClickException("Must specify template type with name")
        click.echo(f'Exporting templates to {file}')
        vmanage_session.export_templates_to_file(file)