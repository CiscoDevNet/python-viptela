"""Cisco vManage SDK CLI.

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
from vmanage.cli.show_cmds import show
from vmanage.cli.apps_cmds import apps
from vmanage.api.authentication import Authentication


class Viptela(object):

    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.auth = Authentication(
            host=host, user=username, password=password).login()


@click.group()
@click.option(
    '--host', envvar='VMANAGE_HOST',
    help='vManage Host (env: VMANAGE_HOST)', required=True
)
@click.option(
    '--username', envvar='VMANAGE_USERNAME',
    help='vManage Username (env: VMANAGE_USERNAME)', required=True
)
@click.option(
    '--password', envvar='VMANAGE_PASSWORD',
    help='vManage Password (env: VMANAGE_PASSWORD)', required=True
)
@click.pass_context
def main(ctx=None, host=None, username=None, password=None):
    ctx.obj = Viptela(host, username, password)


main.add_command(show)
main.add_command(apps)

if __name__ == "__main__":
    main()
