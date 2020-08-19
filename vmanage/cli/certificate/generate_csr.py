import click
from vmanage.api.certificate import Certificate


@click.command('generate-csr')
@click.option('--ip', '-i', help="Device IP address.", required=True)
@click.option('--file', '-f', 'csr_file', help="Output file name", required=True)
@click.pass_obj
def generate_csr(ctx, ip, csr_file):
    """
    Generate CSR for a device
    """

    vmanage_certificate = Certificate(ctx.auth, ctx.host, ctx.port)
    csr = vmanage_certificate.generate_csr(ip)
    with open(csr_file, 'w') as outfile:
        outfile.write(csr)
