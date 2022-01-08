from kintro.plex import sync

import click
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer


@click.group()
@click.option("--user", required=True, help="plex.tv username for server discovery")
@click.option("--password", required=True, prompt=True, hide_input=True, help="plex.tv password")
@click.option("--server", required=True, help="Plex server to use")
@click.pass_context
def account(ctx: click.Context, user: str, password: str, server_loc: str) -> None:

    ctx.obj["logger"].info(f"Connecting to plex via account({user}) and password")
    account_ = MyPlexAccount(user, password)
    ctx.obj["plex"] = account_.resource(server_loc).connect()


@click.group()
@click.option("--url", required=True, help="HTTP(s) url of server with port number")
@click.option("--token", required=True, prompt=True, hide_input=True, help="Plex token")
@click.pass_context
def server(ctx: click.Context, url: str, token: str) -> None:

    ctx.obj["logger"].info(f"Connecting to plex via url({url}) and token")
    ctx.obj["plex"] = PlexServer(url, token)


account.add_command(sync)
server.add_command(sync)
