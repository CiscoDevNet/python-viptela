import click
from vmanage.cli.activate import activate
from vmanage.cli.deactivate import deactivate
from vmanage.cli.show import show
from vmanage.cli.export import export
from vmanage.cli.import_cmd import import_cmd
from vmanage.cli.clean import clean
from vmanage.cli.certificate import certificate
from vmanage.cli.set_cmd import set_cmd
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
    def __init__(self, host, port, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.__auth = None

    # use this to defer authentication until it's needed
    @property
    def auth(self):
        if self.__auth is None:
            self.__auth = Authentication(host=self.host, port=self.port, user=self.username,
                                         password=self.password).login()
        return self.__auth


# @click.group(cls=CatchAllExceptions)
@click.group()
@click.option('--host', envvar='VMANAGE_HOST', help='vManage Host (env: VMANAGE_HOST)', required=True)
@click.option('--port',
              envvar='VMANAGE_PORT',
              help='vManage Port (env: VMANAGE_PORT, default=443)',
              default=443,
              required=False)
@click.option('--username', envvar='VMANAGE_USERNAME', help='vManage Username (env: VMANAGE_USERNAME)', required=True)
@click.option('--password',
              envvar='VMANAGE_PASSWORD',
              prompt=True,
              hide_input=True,
              help='vManage Password (env: VMANAGE_PASSWORD)',
              required=True)
@click.pass_context
def vmanage(ctx, host, port, username, password):
    ctx.obj = Viptela(host, port, username, password)


vmanage.add_command(activate)
vmanage.add_command(deactivate)
vmanage.add_command(show)
vmanage.add_command(export)
vmanage.add_command(import_cmd)
vmanage.add_command(certificate)
vmanage.add_command(clean)
vmanage.add_command(set_cmd)
