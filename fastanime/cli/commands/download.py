from typing import TYPE_CHECKING

import click

from ..completion_functions import anime_titles_shell_complete

if TYPE_CHECKING:
    from ..config import Config


@click.command(
    help="Download anime using the anime provider for a specified range",
    short_help="Download anime",
    epilog="""
\b
\b\bExamples:
  # Download all available episodes
  # multiple titles can be specified with -t option
  fastanime download -t <anime-title> -t <anime-title>
  # -- or --
  fastanime download -t <anime-title> -t <anime-title> -r ':'
\b
  # download latest episode for the two anime titles
  # the number can be any no of latest episodes but a minus sign
  # must be present
  fastanime download -t <anime-title> -t <anime-title> -r '-1'
\b
  # latest 5
  fastanime download -t <anime-title> -t <anime-title> -r '-5'
\b
  # Download specific episode range
  # be sure to observe the range Syntax
  fastanime download -t <anime-title> -r '<episodes-start>:<episodes-end>:<step>'
\b
  fastanime download -t <anime-title> -r '<episodes-start>:<episodes-end>'
\b
  fastanime download -t <anime-title> -r '<episodes-start>:'
\b
  fastanime download -t <anime-title> -r ':<episodes-end>'
\b
  # download specific episode
  # remember python indexing starts at 0
  fastanime download -t <anime-title> -r '<episode-1>:<episode>'
\b
  # merge subtitles with ffmpeg to mkv format; hianime tends to give subs as separate files
  # and dont prompt for anything
  # eg existing file in destination instead remove
  # and clean
  # ie remove original files (sub file and vid file)
  # only keep merged files
  fastanime download -t <anime-title> --merge --clean --no-prompt
\b
  # EOF is used since -t always expects a title
  # you can supply anime titles from file or -t at the same time
  # from stdin
  echo -e "<anime-title>\\n<anime-title>\\n<anime-title>" | fastanime download -t "EOF" -r <range> -f -
\b
  # from file
  fastanime download -t "EOF" -r <range> -f <file-path>
""",
)
@click.option(
    "--anime-titles",
    "--anime_title",
    "-t",
    required=True,
    shell_complete=anime_titles_shell_complete,
    multiple=True,
    help="Specify which anime to download",
)
@click.option(
    "--episode-range",
    "-r",
    help="A range of episodes to download (start-end)",
)
@click.option(
    "--file",
    "-f",
    type=click.File(),
    help="A file to read from all anime to download",
)
@click.option(
    "--force-unknown-ext",
    "-F",
    help="This option forces yt-dlp to download extensions its not aware of",
    is_flag=True,
)
@click.option(
    "--silent/--no-silent",
    "-q/-V",
    type=bool,
    help="Download silently (during download)",
    default=True,
)
@click.option("--verbose", "-v", is_flag=True, help="Download verbosely (everywhere)")
@click.option(
    "--merge", "-m", is_flag=True, help="Merge the subfile with video using ffmpeg"
)
@click.option(
    "--clean",
    "-c",
    is_flag=True,
    help="After merging delete the original files",
)
@click.option(
    "--wait-time",
    "-w",
    type=int,
    help="The amount of time to wait after downloading is complete before the screen is completely cleared",
    default=60,
)
@click.option(
    "--prompt/--no-prompt",
    help="Whether to prompt for anything instead just do the best thing",
    default=True,
)
@click.option(
    "--force-ffmpeg",
    is_flag=True,
    help="Force the use of FFmpeg for downloading (supports large variety of streams but slower)",
)
@click.option(
    "--hls-use-mpegts",
    is_flag=True,
    help="Use mpegts for hls streams, resulted in .ts file (useful for some streams: see Docs) (this option forces --force-ffmpeg to be True)",
)
@click.option(
    "--hls-use-h264",
    is_flag=True,
    help="Use H.264 (MP4) for hls streams, resulted in .mp4 file (useful for some streams: see Docs) (this option forces --force-ffmpeg to be True)",
)
@click.option(
    "--no-check-certificates",
    is_flag=True,
    help="Suppress HTTPS certificate validation",
)
@click.pass_obj
def download(
    config: "Config",
    anime_titles: tuple,
    episode_range,
    file,
    force_unknown_ext,
    silent,
    verbose,
    merge,
    clean,
    wait_time,
    prompt,
    force_ffmpeg,
    hls_use_mpegts,
    hls_use_h264,
    no_check_certificates,
):
    import time

    from rich import print
    from rich.progress import Progress
    from thefuzz import fuzz

    from ...AnimeProvider import AnimeProvider
    from ...libs.anime_provider.types import Anime
    from ...libs.fzf import fzf
    from ...Utility.data import anime_normalizer
    from ...Utility.downloader.downloader import downloader
    from ..utils.tools import exit_app
    from ..utils.utils import (
        filter_by_quality,
        fuzzy_inquirer,
        move_preferred_subtitle_lang_to_top,
    )

    force_ffmpeg |= hls_use_mpegts or hls_use_h264

    anime_provider = AnimeProvider(config.provider)
    anilist_anime_info = None

    translation_type = config.translation_type
    download_dir = config.downloads_dir
    if file:
        contents = file.read()
        anime_titles_from_file = tuple(
            [title for title in contents.split("\n") if title]
        )
        file.close()

        anime_titles = (*anime_titles_from_file, *anime_titles)
    print(f"[green bold]Queued:[/] {anime_titles}")
    for anime_title in anime_titles:
        if anime_title == "EOF":
            break
        print(f"[green bold]Now Downloading: [/] {anime_title}")
        # ---- search for anime ----
        with Progress() as progress:
            progress.add_task("Fetching Search Results...", total=None)
            search_results = anime_provider.search_for_anime(
                anime_title, translation_type=translation_type
            )
        if not search_results:
            print("Search results failed")
            input("Enter to retry")
            download(
                config,
                anime_title,
                episode_range,
                file,
                force_unknown_ext,
                silent,
                verbose,
                merge,
                clean,
                wait_time,
                prompt,
                force_ffmpeg,
                hls_use_mpegts,
                hls_use_h264,
                no_check_certificates,
            )
            return
        search_results = search_results["results"]
        if not search_results:
            print("Nothing muches your search term")
            continue
        search_results_ = {
            search_result["title"]: search_result for search_result in search_results
        }

        if config.auto_select:
            selected_anime_title = max(
                search_results_.keys(),
                key=lambda title: fuzz.ratio(
                    anime_normalizer.get(title, title), anime_title
                ),
            )
            print("[cyan]Auto selecting:[/] ", selected_anime_title)
        else:
            choices = list(search_results_.keys())
            if config.use_fzf:
                selected_anime_title = fzf.run(
                    choices, "Please Select title", "FastAnime"
                )
            else:
                selected_anime_title = fuzzy_inquirer(
                    choices,
                    "Please Select title",
                )

        # ---- fetch anime ----
        with Progress() as progress:
            progress.add_task("Fetching Anime...", total=None)
            anime: Anime | None = anime_provider.get_anime(
                search_results_[selected_anime_title]["id"]
            )
        if not anime:
            print("Sth went wring anime no found")
            input("Enter to continue...")
            download(
                config,
                anime_title,
                episode_range,
                file,
                force_unknown_ext,
                silent,
                verbose,
                merge,
                clean,
                wait_time,
                prompt,
                force_ffmpeg,
                hls_use_mpegts,
                hls_use_h264,
                no_check_certificates,
            )
            return

        episodes = sorted(
            anime["availableEpisodesDetail"][config.translation_type], key=float
        )
        # where the magic happens
        if episode_range:
            if ":" in episode_range:
                ep_range_tuple = episode_range.split(":")
                if len(ep_range_tuple) == 2 and all(ep_range_tuple):
                    episodes_start, episodes_end = ep_range_tuple
                    episodes_range = episodes[int(episodes_start) : int(episodes_end)]
                elif len(ep_range_tuple) == 3 and all(ep_range_tuple):
                    episodes_start, episodes_end, step = ep_range_tuple
                    episodes_range = episodes[
                        int(episodes_start) : int(episodes_end) : int(step)
                    ]
                else:
                    episodes_start, episodes_end = ep_range_tuple
                    if episodes_start.strip():
                        episodes_range = episodes[int(episodes_start) :]
                    elif episodes_end.strip():
                        episodes_range = episodes[: int(episodes_end)]
                    else:
                        episodes_range = episodes
            else:
                episodes_range = episodes[int(episode_range) :]
            print(f"[green bold]Downloading: [/] {episodes_range}")

        else:
            episodes_range = sorted(episodes, key=float)
            print(f"[green bold]Downloading: [/] {episodes_range}")

        if config.normalize_titles:
            from ...libs.common.mini_anilist import get_basic_anime_info_by_title

            anilist_anime_info = get_basic_anime_info_by_title(anime["title"])

        # lets download em
        for episode in episodes_range:
            try:
                episode = str(episode)
                if episode not in episodes:
                    print(f"[cyan]Warning[/]: Episode {episode} not found, skipping")
                    continue
                with Progress() as progress:
                    progress.add_task("Fetching Episode Streams...", total=None)
                    streams = anime_provider.get_episode_streams(
                        anime["id"], episode, config.translation_type
                    )
                    if not streams:
                        print("No streams skipping")
                        continue
                # ---- fetch servers ----
                if config.server == "top":
                    with Progress() as progress:
                        progress.add_task("Fetching top server...", total=None)
                        server_name = next(streams, None)
                        if not server_name:
                            print("Sth went wrong when fetching the server")
                            continue
                    stream_link = filter_by_quality(
                        config.quality, server_name["links"]
                    )
                    if not stream_link:
                        print("[yellow bold]WARNING:[/] No streams found")
                        time.sleep(1)
                        print("Continuing...")
                        continue
                    link = stream_link["link"]
                    provider_headers = server_name["headers"]
                    episode_title = server_name["episode_title"]
                    subtitles = server_name["subtitles"]
                else:
                    with Progress() as progress:
                        progress.add_task("Fetching servers", total=None)
                        # prompt for server selection
                        servers = {server["server"]: server for server in streams}
                    servers_names = list(servers.keys())
                    if config.server in servers_names:
                        server_name = config.server
                    else:
                        if config.use_fzf:
                            server_name = fzf.run(servers_names, "Select an link")
                        else:
                            server_name = fuzzy_inquirer(
                                servers_names,
                                "Select link",
                            )
                    stream_link = filter_by_quality(
                        config.quality, servers[server_name]["links"]
                    )
                    if not stream_link:
                        print("[yellow bold]WARNING:[/] No streams found")
                        time.sleep(1)
                        print("Continuing...")
                        continue
                    link = stream_link["link"]
                    provider_headers = servers[server_name]["headers"]

                    subtitles = servers[server_name]["subtitles"]
                    episode_title = servers[server_name]["episode_title"]

                if anilist_anime_info:
                    selected_anime_title = (
                        anilist_anime_info["title"][config.preferred_language]
                        or anilist_anime_info["title"]["romaji"]
                        or anilist_anime_info["title"]["english"]
                    )
                    import re

                    for episode_detail in anilist_anime_info["episodes"]:
                        if re.match(f"Episode {episode} ", episode_detail["title"]):
                            episode_title = episode_detail["title"]
                            break
                print(f"[purple]Now Downloading:[/] {episode_title}")
                subtitles = move_preferred_subtitle_lang_to_top(
                    subtitles, config.sub_lang
                )
                downloader._download_file(
                    link,
                    selected_anime_title,
                    episode_title,
                    download_dir,
                    silent,
                    vid_format=config.format,
                    force_unknown_ext=force_unknown_ext,
                    verbose=verbose,
                    headers=provider_headers,
                    sub=subtitles[0]["url"] if subtitles else "",
                    merge=merge,
                    clean=clean,
                    prompt=prompt,
                    force_ffmpeg=force_ffmpeg,
                    hls_use_mpegts=hls_use_mpegts,
                    hls_use_h264=hls_use_h264,
                    nocheckcertificate=no_check_certificates,
                )
            except Exception as e:
                print(e)
                time.sleep(1)
                print("Continuing...")
    print("Done Downloading")
    time.sleep(wait_time)
    exit_app()
