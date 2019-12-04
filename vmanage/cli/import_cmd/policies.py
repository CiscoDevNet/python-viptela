    
import click
import pprint

@click.command()
@click.argument('type', default='all')
@click.option('--check/--no-check', help="Just check (no changes)", default=False)
@click.option('--update/--no-update', help="Update if exists", default=False)
@click.option('--push/--no-push', help="Push update (when specifed with --update)", default=False)
@click.option('--diff/--no-diff', help="Show Diffs", default=False)
@click.option('--file', '-f', help="output File name", required=True)
# @click.option('--type',
#               help="Device type [vedges, controllers]",
#               type=click.Choice(['vedges', 'controllers']))
@click.pass_context
def policies(ctx, type, file, update, check, diff, push):
    """
    Import policies from file
    """
    vmanage_session = ctx.obj
    pp = pprint.PrettyPrinter(indent=2)

    click.echo(f"{'Checking' if check else 'Importing'} policies from {file}")
    result = vmanage_session.import_policy_from_file(file, update=update, check_mode=check, push=push)
    print(f"Policy List Updates: {len(result['policy_list_updates'])}")
    if diff:
        for diff_item in result['policy_list_updates']:
            click.echo(f"{diff_item['name']}:")
            pp.pprint(diff_item['diff'])
    print(f"Policy Definition Updates: {len(result['policy_definition_updates'])}")
    if diff:
        for diff_item in result['policy_definition_updates']:
            click.echo(f"{diff_item['name']}:")
            pp.pprint(diff_item['diff'])
    print(f"Central Policy Updates: {len(result['central_policy_updates'])}")
    if diff:
        for diff_item in result['central_policy_updates']:
            click.echo(f"{diff_item['name']}:")
            pp.pprint(diff_item['diff'])
    print(f"Local Policy Updates: {len(result['local_policy_updates'])}")
    if diff:
        for diff_item in result['local_policy_updates']:
            click.echo(f"{diff_item['name']}:")
            pp.pprint(diff_item['diff'])