import pprint

import click
from vmanage.api.central_policy import CentralPolicy
from vmanage.api.local_policy import LocalPolicy
from vmanage.api.policy_definitions import (PolicyDefinitions, all_definition_types)
from vmanage.api.policy_lists import PolicyLists
from vmanage.api.security_policy import SecurityPolicy
from vmanage.cli.show.print_utils import print_json
from vmanage.data.policy_data import PolicyData


@click.command('list')
@click.argument('name', required=False, default=None)
@click.option('--json/--no-json', default=False)
@click.option('--type', '-t', 'policy_list_type', default='all', help="Policy list type")
@click.pass_obj
def list_cmd(ctx, name, json, policy_list_type):  #pylint: disable=unused-argument
    """
    Show policy list information
    """
    policy_lists = PolicyLists(ctx.auth, ctx.host, ctx.port)
    pp = pprint.PrettyPrinter(indent=2)

    if name:
        policy_list_dict = policy_lists.get_policy_list_dict(policy_list_type=policy_list_type)
        if name in policy_list_dict:
            pp.pprint(policy_list_dict[name])
    else:
        policy_lists = policy_lists.get_policy_list_list(policy_list_type=policy_list_type)
        pp.pprint(policy_lists)


@click.command()
@click.argument('name', required=False, default=None)
@click.option('--json/--no-json', default=False)
@click.option('--type',
              '-t',
              'definition_type',
              default='all',
              help="Definition type",
              type=click.Choice(all_definition_types + ['all']))
@click.pass_obj
def definition(ctx, name, json, definition_type):  #pylint: disable=unused-argument
    """
    Show policy definition information
    """
    policy_definitions = PolicyDefinitions(ctx.auth, ctx.host, ctx.port)
    policy_data = PolicyData(ctx.auth, ctx.host, ctx.port)
    pp = pprint.PrettyPrinter(indent=2)

    if name:
        policy_definition_dict = policy_definitions.get_policy_definition_dict(definition_type)
        if name in policy_definition_dict:
            policy_definition = policy_data.export_policy_definition_list(policy_definition_dict[name]['type'].lower())
            # list_keys(policy_definition['definition'])
            pp.pprint(policy_definition)
    else:
        policy_definition_list = policy_data.export_policy_definition_list(definition_type)
        pp.pprint(policy_definition_list)


@click.command()
@click.argument('name', required=False, default=None)
@click.option('--json/--no-json', default=False)
@click.pass_obj
def central(ctx, name, json):  #pylint: disable=unused-argument
    """
    Show central policy information
    """
    central_policy = CentralPolicy(ctx.auth, ctx.host, ctx.port)
    policy_data = PolicyData(ctx.auth, ctx.host, ctx.port)
    pp = pprint.PrettyPrinter(indent=2)

    if name:
        central_policy_dict = central_policy.get_central_policy_dict()
        if name in central_policy_dict:
            if json:
                print_json(central_policy_dict[name])
            else:
                preview = central_policy.get_central_policy_preview(central_policy_dict[name]['policyId'])
                pp.pprint(preview)
    else:
        central_policy_list = policy_data.export_central_policy_list()
        pp.pprint(central_policy_list)


@click.command()
@click.argument('name', required=False, default=None)
@click.option('--json/--no-json', default=False)
@click.pass_obj
def local(ctx, name, json):  #pylint: disable=unused-argument
    """
    Show local policy information
    """
    local_policy = LocalPolicy(ctx.auth, ctx.host, ctx.port)
    policy_data = PolicyData(ctx.auth, ctx.host, ctx.port)
    pp = pprint.PrettyPrinter(indent=2)

    if name:
        policy_list_dict = local_policy.get_policy_list_dict(type=type)
        if name in policy_list_dict:
            pp.pprint(policy_list_dict[name])
    else:
        local_policy_list = policy_data.export_local_policy_list()
        pp.pprint(local_policy_list)


@click.command()
@click.argument('name', required=False, default=None)
@click.option('--json/--no-json', default=False)
@click.pass_obj
def security(ctx, name, json):  #pylint: disable=unused-argument
    """
    Show security policy information
    """
    security_policy = SecurityPolicy(ctx.auth, ctx.host, ctx.port)
    policy_data = PolicyData(ctx.auth, ctx.host, ctx.port)
    pp = pprint.PrettyPrinter(indent=2)

    if name:
        security_policy_dict = security_policy.get_security_policy_dict()
        if name in security_policy_dict:
            if json:
                print_json(security_policy_dict[name])
            else:
                preview = security_policy.get_security_policy_preview(security_policy_dict[name]['policyId'])
                pp.pprint(preview)
    else:
        security_policy_list = policy_data.export_security_policy_list()
        pp.pprint(security_policy_list)


@click.group()
def policies():
    """
    Show policy information
    """


policies.add_command(list_cmd)
policies.add_command(definition)
policies.add_command(central)
policies.add_command(local)
policies.add_command(security)
