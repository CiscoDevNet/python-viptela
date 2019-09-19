    
import click

@click.command()
@click.argument('type', default='all')
@click.option('--check/--no-check', help="Just check (no changes)", default=False)
@click.option('--update/--no-update', help="Update if exists", default=False)
@click.option('--force/--no-force', help="Force change", default=False)
@click.option('--file', '-f', help="output File name", required=True)
# @click.option('--type',
#               help="Device type [vedges, controllers]",
#               type=click.Choice(['vedges', 'controllers']))
@click.pass_context
def policy(ctx, type, file, update, check, force):
    """
    Import policy from file
    """
    vmanage_session = ctx.obj
    click.echo(f'Importing policy from {file}')
    result = vmanage_session.import_policy_from_file(file, update=update, check_mode=check, force=force)
    print(f"Policy List Updates: {result['policy_list_updates']}")
    print(f"Policy Definition Updates: {result['policy_definition_updates']}")
    print(f"Central Policy Updates: {result['central_policy_updates']}")