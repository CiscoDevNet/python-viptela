import click
from vmanage.apps.clean import CleanVmanage


@click.command()
@click.option('--verify-clean/--no-verify-clean', default=False)
@click.pass_obj
def clean(ctx, verify_clean):
    """
    Clean vManage
    """
    clean_vmanage = CleanVmanage(ctx.auth, ctx.host, ctx.port)

    if verify_clean:
        clean_vmanage.clean_all()
    elif click.confirm('This will DESTROY EVERYTHING! Do you want to continue?'):
        clean_vmanage.clean_all()
