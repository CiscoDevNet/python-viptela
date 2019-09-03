    
import click
import pprint

@click.command()
@click.option('--type', help="Template type [device, feature] (default: all)",
              default='all', type=click.Choice(['device', 'feature', 'all']))
@click.option('--name', default=None, help="Show template with name")              
# @click.option('--json/--no-json', help="JSON Output")


@click.pass_context
def templates(ctx, type, name):
    """
    Show template information
    """
    vmanage_session = ctx.obj
    pp = pprint.PrettyPrinter(indent=2)

    if name:
        device_template_dict = vmanage_session.get_device_template_dict()
        if name in device_template_dict:
            pp.pprint(device_template_dict[name])
        feature_template_dict = vmanage_session.get_feature_template_dict()
        if name in feature_template_dict:
            pp.pprint(feature_template_dict[name])            
    else:
        device_template_list = vmanage_session.get_device_template_list()
        if type in ['device', 'all']:
            click.echo(f"{'Name':30} {'Type':20} {'Attached':8} {'Devices'} ")
            for template in device_template_list:
                click.echo(f"{template['templateName']:30} {template['configType']:20} {len(template['attached_devices']):8} {template['deviceType']:12} ")
        feature_template_list = vmanage_session.get_feature_template_list()
        if type in ['feature', 'all']:
            for template in feature_template_list:
                click.echo(f"{template['templateName']:30} {template['templateType']:20} {template['devicesAttached']:8} {','.join(template['deviceType']):20}")