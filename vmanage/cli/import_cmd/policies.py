import pprint

import click
from vmanage.apps.files import Files


@click.command()
@click.option('--file', '-f', 'input_file', help="Input File name", required=True)
@click.option('--check/--no-check', help="Just check (no changes)", default=False)
@click.option('--update/--no-update', help="Update if exists", default=False)
@click.option('--push/--no-push', help="Push update (when specifed with --update)", default=False)
@click.option('--diff/--no-diff', help="Show Diffs", default=False)
@click.pass_obj
def policies(ctx, input_file, check, update, push, diff):
    """
    Import policies from file
    """
    vmanage_files = Files(ctx.auth, ctx.host, ctx.port)
    pp = pprint.PrettyPrinter(indent=2)

    click.echo(f"{'Checking' if check else 'Importing'} policies from {input_file}")
    result = vmanage_files.import_policy_from_file(input_file, update=update, check_mode=check, push=push)
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
    print(f"Security Policy Updates: {len(result['security_policy_updates'])}")
    if diff:
        for diff_item in result['security_policy_updates']:
            click.echo(f"{diff_item['name']}:")
            pp.pprint(diff_item['diff'])
