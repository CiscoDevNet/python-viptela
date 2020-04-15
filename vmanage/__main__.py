import click
from vmanage.cli.activate import activate
from vmanage.cli.deactivate import deactivate
from vmanage.cli.show import show
from vmanage.cli.export import export
from vmanage.cli.import_cmd import import_cmd
from vmanage.cli.certificate import certificate
from vmanage.api.authentication import Authentication

# from vmanage.api.big import vmanage_session


class CatchAllExceptions(click.Group):
    def __call__(self, *args, **kwargs):
        try:
            return self.vmanage(*args, **kwargs)
        except Exception as exc:
            click.secho('Exception raised while running your command', fg="red")
            click.secho("Please open an issue and provide this info:", fg="red")
            click.secho("%s" % exc, fg="red")


class Viptela(object):
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.__auth = None

    # use this to defer authentication until it's needed
    @property
    def auth(self):
        if self.__auth is None:
            self.__auth = Authentication(host=self.host, user=self.username, password=self.password).login()
        return self.__auth


# @click.group(cls=CatchAllExceptions)
@click.group()
@click.option('--host', envvar='VMANAGE_HOST', help='vManage Host (env: VMANAGE_HOST)', required=True)
@click.option('--username', envvar='VMANAGE_USERNAME', help='vManage Username (env: VMANAGE_USERNAME)', required=True)
@click.option('--password',
              envvar='VMANAGE_PASSWORD',
              prompt=True,
              hide_input=True,
              help='vManage Password (env: VMANAGE_PASSWORD)',
              required=True)
@click.pass_context
def vmanage(ctx, host, username, password):
    ctx.obj = Viptela(host, username, password)


vmanage.add_command(activate)
vmanage.add_command(deactivate)
vmanage.add_command(show)
vmanage.add_command(export)
vmanage.add_command(import_cmd)
vmanage.add_command(certificate)
