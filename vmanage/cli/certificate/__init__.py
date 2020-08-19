import click
from vmanage.cli.certificate.push import push
from vmanage.cli.certificate.generate_csr import generate_csr
from vmanage.cli.certificate.install import install


@click.group()
def certificate():
    """
    Certficate commands
    """


certificate.add_command(push)
certificate.add_command(generate_csr)
certificate.add_command(install)
