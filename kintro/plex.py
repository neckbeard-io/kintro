import collections
import concurrent.futures
import enum
import functools
import itertools
import json
import os
import queue
import threading
import time
from typing import (
    Deque,
    List,
)

from kintro.decisions import DECISION_TYPES

import click
from click_option_group import (  # type: ignore[import]
    AllOptionGroup,
    optgroup,
)
import more_itertools
from plexapi.video import Episode  # type: ignore[import]


@enum.unique
class LibType(enum.Enum):
    Episode = "episode"
    Show = "show"


@click.command()
@click.option(
    "--library", required=True, default="TV Shows", help="Plex library to operate on"
)
@click.option(
    "--edit",
    type=click.Choice(["cut", "mute", "scene", "commercial"]),
    default="scene",
    # TODO: convert all this help stuff to docstring format
    help=(
        "cut: Makes it so the intro is completely gone "
        "mute: Makes it so the intro's audio is muted "
        "scene: Makes it so the nextscene action skips to the end of the intro "
        "commercial: Makes it so the intro is skipped once (like cut), but is then seekable after"
    ),
)
@click.option(
    "--dry-run",
    default=False,
    is_flag=True,
    help="Logs the .edl files kintro will write without writing them",
)
@click.option(
    "--libtype",
    default=LibType.Episode.value,
    type=click.Choice([x.name for x in LibType], case_sensitive=False),
    help="type of search to do",
)
@click.option("--filter-json", default=None, help="json representing plex filters")
@optgroup.group(
    "Find and Replace",
    cls=AllOptionGroup,
    help=(
        "Find and Replace options for fixing file paths "
        "(useful for plex servers running in containers)"
    ),
)
@optgroup.option("--find-path", help="Find string")
@optgroup.option(
    "--replace-path", type=click.Path(exists=True), help="Replace directory"
)
@click.option(
    "--max-workers", default=4, help="Max Number of workers to process episodes"
)
@click.option(
    "--worker-batch-size", default=10, help="Chunk of work to hand off to each worker"
)
@click.pass_context
def sync(
    ctx,
    library,
    edit,
    dry_run,
    libtype,
    filter_json,
    find_path,
    replace_path,
    max_workers,
    worker_batch_size,
):
    ctx.obj["logger"].info("Starting sync process")

    plex = ctx.obj["plex"]
    libtype = LibType(libtype.lower())
    edit = DECISION_TYPES[edit]

    more_search = (
        {"filters": json.loads(filter_json)} if filter_json is not None else {}
    )
    tv = {
        LibType.Episode: lambda: plex.library.section(library).search(
            libtype="episode", **more_search
        ),
        LibType.Show: lambda: itertools.chain(
            *(
                show.episodes()
                for show in plex.library.section(library).search(
                    libtype="show",
                    **more_search,
                )
            ),
        ),
    }[libtype]()

    if max_workers == 1:
        for episode in (
            tv
            if worker_batch_size == 1
            else itertools.chain.from_iterable(
                more_itertools.ichunked(tv, worker_batch_size)
            )
        ):
            handle_episode(
                ctx=ctx,
                episode=episode,
                edit=edit,
                find_path=find_path,
                replace_path=replace_path,
                dry_run=dry_run,
            )
    else:
        # Break the TV into yielding iterator chunks for batch processing
        tv_chunked = more_itertools.ichunked(tv, worker_batch_size)

        # Queues for interthread batches and results
        batch_queue = collections.deque()
        results = collections.deque()
        # Events controlling if processing threads are allowed to start or stop
        start_event = threading.Event()
        stop_event = threading.Event()

        def submit():
            ctx.obj["logger"].debug("Putting all episodes in batched queue")
            for episodes in tv_chunked:
                ctx.obj["logger"].debug(f"Putting chunk of episodes in batched queue")
                batch_queue.append(episodes)
                start_event.set()
                time.sleep(0.01)
            start_event.set()
            ctx.obj["logger"].debug("Sending stop event")
            stop_event.set()

        # Start the submitter in a background thread
        ctx.obj["logger"].debug(f"Starting submitter background thread")
        submitter = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        submitter_res = submitter.submit(submit)

        ctx.obj["logger"].debug(
            f"Starting processing pool with max #{max_workers} workers and batch size {worker_batch_size}"
        )
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)

        # Bind all the non varying args for the worker function
        handle_eps = functools.partial(
            handle_episodes,
            ctx=ctx,
            edit=edit,
            find_path=find_path,
            replace_path=replace_path,
            dry_run=dry_run,
            episodes_source=batch_queue,
            results_sink=results,
            start_event=start_event,
            stop_event=stop_event,
        )

        ctx.obj["logger"].debug(
            f"Starting worker fucntions on pool threads (#{max_workers})"
        )
        res = executor.map(
            handle_eps,
            [x for x in range(0, max_workers)],
        )

        ctx.obj["logger"].debug("Requesting the submitter be destroyed")
        submitter.shutdown()
        ctx.obj["logger"].debug("Requesting the worker pool be destroyed")
        executor.shutdown()

        if ctx.obj["debug"]:
            try:
                for r in res:
                    ctx.obj["logger"].debug(f"Worker thread launch result: {r}")
            except Exception as e:
                ctx.obj["logger"].exception(
                    f"Error while checking worker thread status {e}"
                )

            try:
                ctx.obj["logger"].debug(
                    f"Submitter thread status {submitter_res.result()}"
                )
            except Exception as e:
                ctx.obj["logger"].exception(
                    f"Error while checking submitter thread status {e}"
                )

            while True:
                ctx.obj["logger"].debug("Looping on results")
                try:
                    result = results.pop()
                    if len(result) > 0:
                        ctx.obj["logger"].debug(result)
                except IndexError:
                    break


def handle_episodes(
    ix,
    *,
    episodes_source: Deque[List[Episode]],
    results_sink: Deque[List[str]],
    start_event: threading.Event,
    stop_event: threading.Event,
    ctx,
    edit: DECISION_TYPES,
    find_path: str,
    replace_path: str,
    dry_run: bool,
) -> None:
    ctx.obj["logger"].info(
        f"Starting a episodes thread {threading.current_thread().name}"
    )
    ctx.obj["logger"].debug(
        f"Waiting for start event on thread {threading.current_thread().name}"
    )
    start_event.wait()
    ctx.obj["logger"].debug(
        f"Done Waiting for start event on thread {threading.current_thread().name}"
    )
    while True:
        try:
            episodes = list(episodes_source.pop())
            ctx.obj["logger"].debug(
                f"Starting a batch of {len(episodes)} episodes on thread {threading.current_thread().name}"
            )
            for episode in episodes:
                results_sink.append(
                    handle_episode(
                        ctx=ctx,
                        episode=episode,
                        edit=edit,
                        find_path=find_path,
                        replace_path=replace_path,
                        dry_run=dry_run,
                    ),
                )
        except IndexError as e:
            if stop_event.is_set():
                break
            ctx.obj["logger"].debug(
                f"Nothing in queue to process in {threading.current_thread().name} continuing in 1 second"
            )
            time.sleep(1)
        except Exception as e:
            ctx.obj["logger"].warning(
                f"Exception {e} in {threading.current_thread().name} continuing"
            )
            continue
    return None


def handle_episode(
    ctx,
    episode: Episode,
    edit: DECISION_TYPES,
    find_path: str,
    replace_path: str,
    dry_run: bool,
) -> List[str]:
    files_to_modify = []

    ctx.obj["logger"].debug(
        'Checking for intro marker show="%s" season=%s episode=%s title="%s"'
        % (
            episode.grandparentTitle,
            episode.seasonNumber,
            episode.episodeNumber,
            episode.title,
        ),
    )
    # This call is EXTREMELY expensive, do not prefilter on it (this lets threads bear the weight)
    if episode.hasIntroMarker:
        # multiple markers can exist for a file. only want type intro,
        # but it's possible there could be more than one intro
        for marker in episode.markers:
            if marker.type == "intro":
                start = marker.start / 1000
                end = marker.end / 1000
                # build the content for the file
                intro_entry = "%s %s %s" % (start, end, edit.value)
                # plex can expose multiple locations for a video/episode, so we should
                # iterate through them and write an .edl file for each
                for location in episode.locations:
                    file_path = os.path.splitext(location)[0] + ".edl"
                    # if we're running in a container or otherwise need to fix the path
                    if find_path:
                        file_path = file_path.replace(find_path, replace_path)
                    if not dry_run:
                        with open(file_path, "w") as writer:
                            writer.write(intro_entry)

                    files_to_modify.append(file_path)

                    ctx.obj["logger"].info(
                        'show="%s" season=%s episode=%s title="%s" location="%s start=%s end=%s file="%s"'
                        % (
                            episode.grandparentTitle,
                            episode.seasonNumber,
                            episode.episodeNumber,
                            episode.title,
                            episode.locations,
                            start,
                            end,
                            file_path,
                        ),
                    )

    return files_to_modify
