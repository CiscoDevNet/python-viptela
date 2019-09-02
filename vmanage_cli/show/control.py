import click
import pprint

@click.command()
@click.argument('device_ip', required=True)
# @click.option('--device_ip', default='', help="Show information for device")
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

    click.echo("                                                           PEER                  PEER                                           CONTROLLER")
    click.echo("PEER    PEER PEER            SITE   DOMAIN PEER            PRIV  PEER            PUB                                            GROUP")
    click.echo("TYPE    PROT SYSTEM IP       ID     ID     PRIVATE IP      PORT  PUBLIC IP       PORT  LOCAL COLOR      PROXY STATE UPTIME      ID")
    click.echo("------------------------------------------------------------------------------------------------------------------------------------------")
#vsmart  dtls 3.3.3.3         3          1      172.20.1.12                             12346 172.20.1.12                             12346 public-internet No    up     3:06:45:41  0
#vbond   dtls 0.0.0.0         0          0      172.20.1.11                             12346 172.20.1.11                             12346 public-internet -     up     3:06:46:23  0
#vmanage dtls 1.1.1.1         1          0      172.20.1.10                             12546 172.20.1.10                             12546 public-internet No    up     3:06:46:23  0
    pp = pprint.PrettyPrinter(indent=2)
    for connection in control_connections:
        if json:
            pp.pprint(connection)
        else :
            click.echo(f"{connection['peer-type']:7} {connection['protocol']:4} {connection['system-ip']:15} {connection['site-id']:6} {connection['domain-id']:6} {connection['private-ip']:15} {connection['private-port']:5} {connection['public-ip']:15} {connection['public-port']:5} {connection['local-color']:15}  {connection['state']:11} {connection['uptime']:11} {connection['controller-group-id']}")

@click.group()
@click.pass_context
def control(ctx):
    """
    OMP commands
    """

control.add_command(connections)

