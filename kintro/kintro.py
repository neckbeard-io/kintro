from plexapi.myplex import MyPlexAccount
from kintro.decisions import DECISION_TYPES
from click_option_group import optgroup, AllOptionGroup

import click
import enum
import itertools
import json
import logging
import os
import sys

@enum.unique
class LibType(enum.Enum):
    Episode = 'episode'
    Show = 'show'


@click.command()
@click.option('--user', required=True, help='plex.tv username for server discovery')
@click.option('--password', required=True, help='plex.tv password')
@click.option('--server', required=True, help='Plex server to use')
@click.option('--library', required=True, default='TV Shows', help='Plex library to operate on')
@click.option(
    '--edit',
    type=click.Choice(['cut', 'mute', 'scene', 'commercial']),
    default='scene',
    #TODO: convert all this help stuff to docstring format
    help='cut: Makes it so the intro is completely gone ' \
         'mute: Makes it so the intro\'s audio is muted ' \
         'scene: Makes it so the nextscene action skips to the end of the intro ' \
         'commercial: Makes it so the intro is skipped once (like cut), but is then seekable after'
)
@click.option('--dry-run', default=False, is_flag=True, help='Logs the .edl files kintro will write without writing them')
@click.option(
    '--libtype',
    default=LibType.Episode.value,
    type=click.Choice((x.name for x in LibType), case_sensitive=False),
    help='type of search to do',
)
@click.option('--filter-json', default=None, help='json representing plex filters')
@optgroup.group(
    'Find and Replace',
    cls=AllOptionGroup,
    help='Find and Replace options for fixing file paths '
         '(useful for plex servers running in containers)'
)
@optgroup.option('--find-path', help='Find string')
@optgroup.option('--replace-path', type=click.Path(exists=True), help='Replace directory')

def cli(user, password, server, library, edit, dry_run, libtype, filter_json, find_path, replace_path):
    libtype = LibType(libtype.lower())
    formatter = logging.Formatter(
        fmt=(
            '%(asctime)s %(filename)-15s %(funcName)-20s '
            '%(levelname)-7s %(message)s'
        ),
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger('kintro')
    logger.setLevel(logging.INFO)
    logger.addHandler(screen_handler)

    account = MyPlexAccount(user, password)
    plex = account.resource(server).connect()
    more_search = {'filters': json.loads(filter_json)} if filter_json is not None else {}
    tv = {
        LibType.Episode: lambda: plex.library.section(library).search(libtype='episode', **more_search),
        LibType.Show: lambda: itertools.chain(*(show.episodes() for show in plex.library.section(library).search(libtype='show', **more_search))),
    }[libtype]()

    for episode in tv:
        if episode.hasIntroMarker:
            # multiple markers can exist for a file. only want type intro,
            # but it's possible there could be more than one intro
            decisions = []
            for marker in episode.markers:
                if marker.type == 'intro':
                    start = marker.start / 1000
                    end = marker.end / 1000
                    # build the content for the file
                    intro_entry = '%s %s %s' % (start, end, DECISION_TYPES[edit])
                    # plex can expose multiple locations for a video/episode, so we should
                    # iterate through them and write an .edl file for each
                    for location in episode.locations:
                        file_path = os.path.splitext(location)[0] + '.edl'
                        # if we're running in a container or otherwise need to fix the path
                        if find_path:
                            file_path = file_path.replace(find_path, replace_path)
                        if not dry_run:
                            with open(file_path, 'w') as writer:
                                writer.write(intro_entry)
                        logger.info(
                            'show="%s" season=%s episode=%s title="%s" location="%s start=%s end=%s file="%s"' %
                            (episode.grandparentTitle, episode.seasonNumber, episode.episodeNumber,
                             episode.title, episode.locations, start, end, file_path)
                        )


