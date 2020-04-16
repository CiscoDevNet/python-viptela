import click
from vmanage.apps.files import Files


@click.command()
@click.option('--file', '-f', 'input_file', help="Input file name", required=True)
@click.option('--check/--no-check', help="Just check (no changes)", default=False)
@click.option('--update/--no-update', help="Update if exists", default=False)
# @click.option('--diff/--no-diff', help="Show Diffs", default=False)
@click.option('--name', '-n', multiple=True)
@click.option('--type',
              '-t',
              'template_type',
              help="Template type",
              type=click.Choice(['device', 'feature']),
              default=None)
@click.pass_obj
def attachments(ctx, input_file, check, update, name, template_type):
    """
    Import attachments from file
    """
    vmanage_files = Files(ctx.auth, ctx.host)

    click.echo(f'Importing attachments from {input_file}')
    result = vmanage_files.import_attachments_from_file(input_file,
                                                        update=update,
                                                        check_mode=check,
                                                        name_list=name,
                                                        template_type=template_type)
    print(f"Attachment Updates: {len(result['updates'])}")
    for host, failure in result['failures'].items():
        click.secho(f"{host}: {failure}", err=True, fg='red')
