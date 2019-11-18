    
import click
import pprint
import dictdiffer

@click.command()
@click.option('--type', '-t',
               help="Template type",
               type=click.Choice(['device', 'feature']),
               default=None)
@click.option('--diff', help="Diff with template of specified name", default=None)
@click.option('--default/--no-default', help="Print system default templates", default=False)
@click.option('--name', '-n')          
@click.option('--json/--no-json', help="JSON Output")
@click.pass_context
def templates(ctx, type, name, diff, default, json):
    """
    Show template information
    """
    vmanage_session = ctx.obj
    pp = pprint.PrettyPrinter(indent=2)

    if name:
        if type == 'device':
            template_list = vmanage_session.get_device_template_list(name_list=[name])
        elif type == 'feature':
            template_list = vmanage_session.get_feature_template_list(name_list=[name])
        else:
            raise click.ClickException("Must specify template type with name")
        template = template_list[0] if template_list else None
        
        if template:
            if diff:
                diff_template = {}
                if type == 'device':
                    diff_template_list = vmanage_session.get_device_template_list(name_list=[diff])
                    if diff_template_list:
                        diff_template = diff_template_list[0]
                    else:
                        click.secho(f"Cannot find device template {diff}", fg="red")
                elif type == 'feature':
                    diff_template_list = vmanage_session.get_feature_template_list(name_list=[diff])
                    if diff_template_list:
                        diff_template = diff_template_list[0]
                    else:
                        click.secho(f"Cannot find feature template {diff}", fg="red")
                else:
                    # Should not get here
                    raise click.ClickException(f"Unknown template type {type}")
                if diff_template:
                    diff = dictdiffer.diff(template, diff_template)
                    pp.pprint(list(diff))
            else:
                pp.pprint(template)
        else:
            click.secho(f"Cannot find template named {name}", fg="red")   
    else:
        if type in ['device', None]:
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
        if type in ['feature', None]:
            feature_template_list = vmanage_session.get_feature_template_list(factory_default=default)
            if not json:
                click.echo("                                                    DEVICE     DEVICES   DEVICE")
                click.echo("NAME                           TYPE                 TEMPLATES  ATTACHED  MODELS")
                click.echo("------------------------------------------------------------------------------------")
                for template in feature_template_list:
                    click.echo(f"{template['templateName'][:30]:30} {template['templateType'][:20]:20} {template['attachedMastersCount']:<10} {template['devicesAttached']:<9} {','.join(template['deviceType'])[:16]:16}")
            else:
                pp.pprint(feature_template_list)

