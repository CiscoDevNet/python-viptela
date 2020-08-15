import pprint

import click
from vmanage.apps.files import Files


@click.command()
@click.option('--file', '-f', 'input_file', help="Input File name", required=True)
@click.option('--check/--no-check', help="Just check (no changes)", default=False)
@click.option('--update/--no-update', help="Update if exists", default=False)
@click.option('--diff/--no-diff', help="Show Diffs", default=False)
@click.option('--name', '-n', multiple=True)
@click.option('--type',
              '-t',
              'template_type',
              help="Template type",
              type=click.Choice(['device', 'feature']),
              default=None)
@click.pass_obj
def templates(ctx, input_file, check, update, diff, name, template_type):
    """
    Import templates from file
    """
    vmanage_files = Files(ctx.auth, ctx.host, ctx.port)
    pp = pprint.PrettyPrinter(indent=2)

    click.echo(f'Importing templates from {input_file}')
    result = vmanage_files.import_templates_from_file(input_file,
                                                      update=update,
                                                      check_mode=check,
                                                      name_list=name,
                                                      template_type=template_type)
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
