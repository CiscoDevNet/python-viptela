"""Cisco vManage SDK Show Commands.

MIT License

Copyright (c) 2019 Cisco Systems and/or its affiliates.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import click
import pprint
from vmanage.api.monitor_network import MonitorNetwork

PP = pprint.PrettyPrinter(indent=2)

@click.command()
@click.option(
    '--sysip', help='System IP',
    default=None, required=True
)
@click.pass_obj
def control_connections(ctx, sysip):
    """
    Show control connections
    """
    mn = MonitorNetwork(ctx.auth, ctx.host)
    output = mn.get_control_connections(sysip)
    PP.pprint(output)

@click.command()
@click.option(
    '--sysip', help='System IP',
    default=None, required=True
)
@click.pass_obj
def control_connections_history(ctx, sysip):
    """
    Show control connections-history
    """
    mn = MonitorNetwork(ctx.auth, ctx.host)
    output = mn.get_control_connections_history(sysip)
    PP.pprint(output)

@click.command()
@click.option(
    '--sysip', help='System IP',
    default=None, required=True
)
@click.pass_obj
def device_status(ctx, sysip):
    """
    Show device status
    """
    mn = MonitorNetwork(ctx.auth, ctx.host)
    output = mn.get_device_status(sysip)
    PP.pprint(output)

@click.group()
@click.pass_context
def show(ctx):
    """
    Real-Time Network Monitoring
    """

show.add_command(control_connections)
show.add_command(control_connections_history)
show.add_command(device_status)
