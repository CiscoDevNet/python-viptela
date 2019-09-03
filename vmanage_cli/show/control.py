import click
import pprint

@click.command()
# @click.argument('device_ip', required=True)
# @click.option('--device_ip', default='', help="Show information for device")
@click.option('--device_ip', default=None, required=True)
@click.option('--json/--no-json', default=False)
# @click.option('--type', default='all',
#                help="Device type [vedges, controllers]",
#                type=click.Choice(['vedges', 'controllers', 'all']))
@click.pass_context
def connections(ctx, device_ip, json):
    """
    Show device information
    """

    vmanage_session = ctx.obj
    control_connections = vmanage_session.get_control_connections(device_ip)

    if json:
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(control_connections)
    else:
        click.echo("PEER    PEER PEER            SITE   DOMAIN PEER            PEER            ")        
        click.echo("TYPE    PROT SYSTEM IP       ID     ID     PRIVATE IP      PUBLIC IP       LOCAL COLOR      PROXY STATE UPTIME")
        click.echo("-------------------------------------------------------------------------------------------------------------------")
        for connection in control_connections:
            click.echo(f"{connection['peer-type']:7} {connection['protocol']:4} {connection['system-ip']:15} {connection['site-id']:6} {connection['domain-id']:6} {connection['private-ip']:15} {connection['public-ip']:15} {connection['local-color']:15}  {connection['state']:11} {connection['uptime']:11}")

@click.group()
@click.pass_context
def control(ctx):
    """
    OMP commands
    """

control.add_command(connections)

