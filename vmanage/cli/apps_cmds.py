"""Cisco vManage SDK Applications Commands.

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
from vmanage.apps.reset_vmanage import ResetVmanage

PP = pprint.PrettyPrinter(indent=2)
CONFIRMATION = 'I understand the consequences'

@click.command()
@click.option(
    '--confirm', help='"I understand the consequences"',
    prompt=(
      'To confirm this action please type the following:\n'
      '"I understand the consequences"\n'
      'Enter confirmation phrase'
    )
)
@click.pass_obj
def reset_vmanage(ctx, confirm):
    """
    (WARNING) Reset vManage by Erasing All Configurations
    """
    if confirm == CONFIRMATION:
        rm = ResetVmanage(ctx.auth, ctx.host)
        output = rm.execute()
        PP.pprint(output)
    else:
        PP.pprint('Incorrect entry or command aborted')

@click.group()
@click.pass_context
def apps(ctx):
    """
    Execute SDK Applications for vManage
    """

apps.add_command(reset_vmanage)
