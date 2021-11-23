from kintro.connect import account, server
from kintro.utils import _init_logger

import click


@click.group()
@click.version_option()
@click.pass_context
def cli(ctx):

    ctx.obj = {}
    ctx.obj['logger'] = _init_logger('kintro')

cli.add_command(account)
cli.add_command(server)