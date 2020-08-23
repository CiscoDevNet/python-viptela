import click
from vmanage.apps.files import Files


@click.command()
@click.option('--file', '-f', 'input_file', help="Input file name", required=True)
@click.option('--check/--no-check', help="Just check (no changes)", default=False)
@click.option('--update/--no-update', help="Update if exists", default=False)
# @click.option('--diff/--no-diff', help="Show Diffs", default=False)
@click.option('--name', '-n', help="Host name of the device", multiple=True)
@click.pass_obj
def attachments(ctx, input_file, check, update, name):
    """
    Import attachments from file
    """
    vmanage_files = Files(ctx.auth, ctx.host, ctx.port)

    if name:
        click.echo(f'Importing attachment(s) for {",".join(name)} from {input_file}')
        result = vmanage_files.import_attachments_from_file(input_file, update=update, check_mode=check, name_list=name)
    else:
        click.echo(f'Importing attachment(s) from {input_file}')
        result = vmanage_files.import_attachments_from_file(input_file, update=update, check_mode=check)

    print(f"Attachment Updates: {len(result['updates'])}")
    for host, failure in result['failures'].items():
        click.secho(f"{host}: {failure}", err=True, fg='red')
