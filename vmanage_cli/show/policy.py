import click
import pprint

@click.command()
@click.argument('name', required=False, default=None)
@click.option('--json/--no-json', default=False)
@click.option('--type', default='all',
               help="Policy list type")
@click.pass_context
def list(ctx, name, type, json):
    """
    Show policy list information
    """
    vmanage_session = ctx.obj
    pp = pprint.PrettyPrinter(indent=2)

    if name:
        policy_list_dict = vmanage_session.get_policy_list_dict(type=type)
        if name in policy_list_dict:
            pp.pprint(policy_list_dict[name])
    else:
        policy_lists = vmanage_session.get_policy_list_list(type=type)
        pp.pprint(policy_lists)

@click.command()
@click.argument('name', required=False, default=None)
@click.option('--json/--no-json', default=False)
@click.option('--type', default='all',
               help="Device type [vedges, controllers]",
               type=click.Choice(['vedges', 'controllers', 'all']))
@click.pass_context
def definition(ctx, name, type, json):
    """
    Show policy definition information
    """
    vmanage_session = ctx.obj
    pp = pprint.PrettyPrinter(indent=2)

    if name:
        policy_list_dict = vmanage_session.get_policy_list_dict(type=type)
        if name in policy_list_dict:
            pp.pprint(policy_list_dict[name])
    else:
        policy_definition_list = vmanage_session.get_policy_definition_list(type=type)
        pp.pprint(policy_definition_list) 

@click.command()
@click.argument('name', required=False, default=None)
@click.option('--json/--no-json', default=False)
@click.pass_context
def central(ctx, name, json):
    """
    Show central policy information
    """
    vmanage_session = ctx.obj
    pp = pprint.PrettyPrinter(indent=2)

    if name:
        central_policy_dict = vmanage_session.get_central_policy_dict()
        if name in central_policy_dict:
            if json:
                pp.pprint(central_policy_dict[name])
            else:
                preview = vmanage_session.get_central_policy_preview(central_policy_dict[name]['policyId'])
                pp.pprint(preview)
    else:
        central_policy_list = vmanage_session.get_central_policy_list()
        pp.pprint(central_policy_list) 

@click.command()
@click.argument('name', required=False, default=None)
@click.option('--json/--no-json', default=False)
@click.pass_context
def local(ctx, name, json):
    """
    Show local policy information
    """
    vmanage_session = ctx.obj
    pp = pprint.PrettyPrinter(indent=2)

    if name:
        policy_list_dict = vmanage_session.get_policy_list_dict(type=type)
        if name in policy_list_dict:
            pp.pprint(policy_list_dict[name])
    else:
        local_policy_list = vmanage_session.get_local_policy_list()
        pp.pprint(local_policy_list) 

@click.group()
@click.pass_context
def policy(ctx):
    """
    OMP commands
    """

policy.add_command(list)
policy.add_command(definition)
policy.add_command(central)
policy.add_command(local)