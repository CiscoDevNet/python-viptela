import click
from vmanage.apps.clean import CleanVmanage


@click.command()
@click.option('--verify_clean/--no-verify_clean', default=False)
# @click.option('--type',
#               '-t',
#               'template_type',
#               multiple=True
#               help="Template type",
#               type=click.Choice(['device', 'feature']),
#               default=None)
@click.pass_obj
def clean(ctx, verify_clean):
    """
    Clean vManage
    """
    clean_vmanage = CleanVmanage(ctx.auth, ctx.host)

    if verify_clean:
        clean_vmanage.clean_all()
