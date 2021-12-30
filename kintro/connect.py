from kintro.plex import sync
from plexapi.myplex import MyPlexAccount # type: ignore[import]
from plexapi.server import PlexServer # type: ignore[import]

import click


@click.group()
@click.option('--user', required=True, help='plex.tv username for server discovery')
@click.option('--password', required=True, prompt=True, hide_input=True, help='plex.tv password')
@click.option('--server', required=True, help='Plex server to use')
@click.pass_context
def account(ctx, user, password, server):

    ctx.obj['logger'].info(f'Connecting to plex via account({user}) and password')
    account = MyPlexAccount(user, password)
    ctx.obj['plex'] = account.resource(server).connect()

@click.group()
@click.option('--url', required=True, help='HTTP(s) url of server with port number')
@click.option('--token', required=True, prompt=True, hide_input=True, help='Plex token')
@click.pass_context
def server(ctx, url, token):

    ctx.obj['logger'].info(f'Connecting to plex via url({url}) and token')
    ctx.obj['plex'] = PlexServer(url, token)

account.add_command(sync)
server.add_command(sync)
