    
import click
import pprint
import dictdiffer

@click.command()
@click.option('--type', help="Template type [device, feature] (default: all)",
              default='all', type=click.Choice(['device', 'feature', 'all']))
@click.option('--diff', help="Diff with template of specified name", default=None)
@click.option('--default/--no-default', help="Print system default templates")
@click.argument('name', default=None, required=False)          
@click.option('--json/--no-json', help="JSON Output")
@click.pass_context
def template(ctx, type, name, diff, default, json):
    """
    Show template information
    """
    vmanage_session = ctx.obj
    pp = pprint.PrettyPrinter(indent=2)

    if name:
        template = {}
        template_type = None
        device_template_dict = vmanage_session.get_device_template_dict()
        if name in device_template_dict:
            template_type = 'device'
            template = device_template_dict[name]
        feature_template_dict = vmanage_session.get_feature_template_dict()
        if name in feature_template_dict:
            template_type = 'feature'
            template = feature_template_dict[name]
        if template:
            if diff:
                diff_template = {}
                if template_type == 'device':
                    if diff in device_template_dict:
                        diff_template = device_template_dict[diff]
                    else:
                        click.secho(f"Cannot find device template named {diff}", fg="red")
                elif template_type == 'feature':
                    if diff in feature_template_dict:
                        diff_template = feature_template_dict[diff]
                    else:
                        click.secho(f"Cannot find device template named {diff}", fg="red") 
                else:
                    # Need to handle CLI
                    pass
                if diff_template:
                    diff = dictdiffer.diff(template, diff_template)
                    pp.pprint(list(diff))
            else:
                pp.pprint(template)
        else:
            click.secho(f"Cannot find template named {name}", fg="red")   
    else:
        if type in ['device', 'all']:
            device_template_list = vmanage_session.get_device_template_list(factory_default=default)
            if not json:
                click.echo("                                          DEVICES")
                click.echo("NAME                           TYPE       ATTACHED  DEVICE TYPES")
                click.echo("--------------------------------------------------------------------------")
                for template in device_template_list:
                    click.echo(f"{template['templateName'][:30]:30} {template['configType'][:10]:10} {len(template['attached_devices']):<9} {template['deviceType'][:16]:16} ")
                click.echo()
            else:
                pp.pprint(device_template_list)
        if type in ['feature', 'all']:
            feature_template_list = vmanage_session.get_feature_template_list(factory_default=default)
            if not json:
                click.echo("                                                    DEVICE     DEVICES   DEVICE")
                click.echo("NAME                           TYPE                 TEMPLATES  ATTACHED  MODELS")
                click.echo("------------------------------------------------------------------------------------")
                for template in feature_template_list:
                    click.echo(f"{template['templateName'][:30]:30} {template['templateType'][:20]:20} {template['attachedMastersCount']:<10} {template['devicesAttached']:<9} {','.join(template['deviceType'])[:16]:16}")
            else:
                pp.pprint(feature_template_list)

