import click
import pprint
from vmanage.apps.files import Files


@click.command()
@click.argument('type', default='all')
@click.option('--check/--no-check', help="Just check (no changes)", default=False)
@click.option('--update/--no-update', help="Update if exists", default=False)
@click.option('--diff/--no-diff', help="Show Diffs", default=False)
@click.option('--file', '-f', help="output File name", required=True)
@click.option('--name', '-n', multiple=True)
@click.option('--type', '-t',
              help="Template type",
              type=click.Choice(['device', 'feature']),
              default=None)
@click.pass_obj
def templates(ctx, file, update, check, diff, name, type):
    """
    Import templates from file
    """
    vmanage_files = Files(ctx.auth, ctx.host)
    pp = pprint.PrettyPrinter(indent=2)

    click.echo(f'Importing templates from {file}')
    result = vmanage_files.import_templates_from_file(file, update=update, check_mode=check, name_list=name, type=type)
    print(f"Feature Template Updates: {len(result['feature_template_updates'])}")
    if diff:
        for diff_item in result['feature_template_updates']:
            click.echo(f"{diff_item['name']}:")
            pp.pprint(diff_item['diff'])
    print(f"Device Template Updates: {len(result['device_template_updates'])}")
    if diff:
        for diff_item in result['device_template_updates']:
            click.echo(f"{diff_item['name']}:")
            pp.pprint(diff_item['diff'])
