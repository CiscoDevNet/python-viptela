import pprint

import click
import dictdiffer
from vmanage.api.device_templates import DeviceTemplates
from vmanage.api.feature_templates import FeatureTemplates
from vmanage.cli.show.print_utils import print_json
from vmanage.data.template_data import TemplateData


@click.command()
@click.option('--type',
              '-t',
              'template_type',
              help="Template type",
              type=click.Choice(['device', 'feature']),
              default=None)
@click.option('--diff', help="Diff with template of specified name", default=None)
@click.option('--default/--no-default', help="Print system default templates", default=False)
@click.option('--name', '-n')
@click.option('--json/--no-json', help="JSON Output")
@click.pass_obj
def templates(ctx, template_type, diff, default, name, json):
    """
    Show template information
    """
    device_templates = DeviceTemplates(ctx.auth, ctx.host, ctx.port)
    feature_templates = FeatureTemplates(ctx.auth, ctx.host, ctx.port)
    template_data = TemplateData(ctx.auth, ctx.host, ctx.port)
    pp = pprint.PrettyPrinter(indent=2)

    if name:
        if template_type == 'device':
            template_list = template_data.export_device_template_list(name_list=[name])
        elif template_type == 'feature':
            template_list = feature_templates.get_feature_template_list(name_list=[name])
        else:
            raise click.ClickException("Must specify template type with name")
        template = template_list[0] if template_list else None

        if template:
            if diff:
                diff_template = {}
                if template_type == 'device':
                    diff_template_list = template_data.export_device_template_list(name_list=[diff])
                    if diff_template_list:
                        diff_template = diff_template_list[0]
                    else:
                        click.secho(f"Cannot find device template {diff}", fg="red")
                elif template_type == 'feature':
                    diff_template_list = feature_templates.get_feature_template_list(name_list=[diff])
                    if diff_template_list:
                        diff_template = diff_template_list[0]
                    else:
                        click.secho(f"Cannot find feature template {diff}", fg="red")
                else:
                    # Should not get here
                    raise click.ClickException(f"Unknown template type {template_type}")
                if diff_template:
                    diff_ignore = set([
                        'templateId', 'policyId', 'connectionPreferenceRequired', 'connectionPreference',
                        'templateName', 'attached_devices', 'input'
                    ])
                    diff = dictdiffer.diff(template, diff_template, ignore=diff_ignore)
                    pp.pprint(list(diff))
            else:
                print_json(template)
        else:
            click.secho(f"Cannot find template named {name}", fg="red")
    else:
        if template_type in ['device', None]:
            device_template_list = template_data.export_device_template_list(factory_default=default)
            if not json:
                click.echo("                                          DEVICES")
                click.echo("NAME                           TYPE       ATTACHED  DEVICE TYPES")
                click.echo("--------------------------------------------------------------------------")
                for template in device_template_list:
                    attached_devices = device_templates.get_template_attachments(template['templateId'])
                    click.echo(
                        f"{template['templateName'][:30]:30} {template['configType'][:10]:10} {len(attached_devices):<9} "
                        f"{template['deviceType'][:16]:16} ")
                click.echo()
            else:
                print_json(device_template_list)
        if template_type in ['feature', None]:
            feature_template_list = feature_templates.get_feature_template_list(factory_default=default)
            if not json:
                click.echo("                                                    DEVICE     DEVICES   DEVICE")
                click.echo("NAME                           TYPE                 TEMPLATES  ATTACHED  MODELS")
                click.echo("------------------------------------------------------------------------------------")
                for template in feature_template_list:
                    click.echo(
                        f"{template['templateName'][:30]:30} {template['templateType'][:20]:20} {template['attachedMastersCount']:<10} "
                        f"{template['devicesAttached']:<9} {','.join(template['deviceType'])[:16]:16}")
            else:
                print_json(feature_template_list)
