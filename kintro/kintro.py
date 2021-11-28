from kintro.connect import account, server
from kintro.utils import _init_logger

import click
import logging


@click.group()
@click.version_option()
@click.option(
    '--log-level',
    default='info',
    type=click.Choice(['debug', 'info', 'warning', 'error']),
    help='Set the minimum log level'
)
@click.pass_context
def cli(ctx, log_level):

    log_level = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
    }[log_level.lower()]

    ctx.obj = {}
    ctx.obj['logger'] = _init_logger('kintro', log_level)

cli.add_command(account)
cli.add_command(server)
