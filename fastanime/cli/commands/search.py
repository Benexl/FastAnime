from typing import TYPE_CHECKING

import click

from ..completion_functions import anime_titles_shell_complete

if TYPE_CHECKING:
    from ...cli.config import Config


@click.command(
    help="This subcommand directly interacts with the provider to enable basic streaming. Useful for binging anime.",
    short_help="Binge anime",
    epilog="""
\b
\b\bExamples:
  # basic form where you will still be prompted for the episode number
  # multiple titles can be specified with the -t option
  fastanime search -t <anime-title> -t <anime-title>
\b
  # binge all episodes with this command
  fastanime search -t <anime-title> -r ':'
\b
  # watch latest episode
  fastanime search -t <anime-title> -r '-1'
\b
  # binge a specific episode range with this command
  # be sure to observe the range Syntax
  fastanime search -t <anime-title> -r '<start>:<stop>'
\b
  fastanime search -t <anime-title> -r '<start>:<stop>:<step>'
\b
  fastanime search -t <anime-title> -r '<start>:'
\b
  fastanime search -t <anime-title> -r ':<end>'
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
    help="A range of episodes to binge (start-end)",
)
@click.pass_obj
def search(config: "Config", anime_titles: str, episode_range: str):
    from click import clear
    from rich import print
    from rich.progress import Progress
    from thefuzz import fuzz

    from ...libs.fzf import fzf
    from ...libs.rofi import Rofi
    from ..utils.tools import exit_app
    from ..utils.utils import fuzzy_inquirer

    if config.manga:
        from InquirerPy.prompts.number import NumberPrompt
        from yt_dlp.utils import sanitize_filename

        from ...MangaProvider import MangaProvider

        from ..utils.feh import feh_manga_viewer
        from ..utils.icat import icat_manga_viewer

        manga_title = anime_titles[0]

        manga_provider = MangaProvider()
        search_data = manga_provider.search_for_manga(manga_title)
        if not search_data:
            print("No search results")
            exit(1)

        search_results = search_data["results"]

        search_results_ = {
            sanitize_filename(search_result["title"]): search_result
            for search_result in search_results
        }

        if config.auto_select:
            search_result_manga_title = max(
                search_results_.keys(),
                key=lambda title: fuzz.ratio(title, manga_title),
            )
            print("[cyan]Auto Selecting:[/] ", search_result_manga_title)

        else:
            choices = list(search_results_.keys())
            preview = None
            if config.preview:
                from ..interfaces.utils import get_fzf_manga_preview

                preview = get_fzf_manga_preview(search_results)
            if config.use_fzf:
                search_result_manga_title = fzf.run(
                    choices, "Please Select title", preview=preview
                )
            elif config.use_rofi:
                search_result_manga_title = Rofi.run(choices, "Please Select Title")
            else:
                search_result_manga_title = fuzzy_inquirer(
                    choices,
                    "Please Select Title",
                )

        anilist_id = search_results_[search_result_manga_title]["id"]
        manga_info = manga_provider.get_manga(anilist_id)
        if not manga_info:
            print("No manga info")
            exit(1)

        anilist_helper = None
        if config.user:
            from ...anilist import AniList

            AniList.login_user(config.user["token"])
            anilist_helper = AniList

        def _manga_viewer():
            chapter_number = NumberPrompt("Select a chapter number").execute()
            chapter_info = manga_provider.get_chapter_thumbnails(
                manga_info["id"], str(chapter_number)
            )

            if not chapter_info:
                print("No chapter info")
                input("Enter to retry...")
                _manga_viewer()
                return
            print(
                f"[purple bold]Now Reading: [/] {search_result_manga_title} [cyan bold]Chapter:[/] {chapter_info['title']}"
            )
            if config.manga_viewer == "feh":
                feh_manga_viewer(chapter_info["thumbnails"], str(chapter_info["title"]))
            elif config.manga_viewer == "icat":
                icat_manga_viewer(
                    chapter_info["thumbnails"], str(chapter_info["title"])
                )
            if anilist_helper:
                anilist_helper.update_anime_list(
                    {"mediaId": anilist_id, "progress": chapter_number}
                )
            _manga_viewer()

        _manga_viewer()
    else:
        from ...AnimeProvider import AnimeProvider
        from ...libs.anime_provider.types import Anime
        from ...Utility.data import anime_normalizer
        from ..utils.mpv import run_mpv
        from ..utils.utils import filter_by_quality, move_preferred_subtitle_lang_to_top

        anime_provider = AnimeProvider(config.provider)
        anilist_anime_info = None

        print(f"[green bold]Streaming:[/] {anime_titles}")
        for anime_title in anime_titles:
            # ---- search for anime ----
            with Progress() as progress:
                progress.add_task("Fetching Search Results...", total=None)
                search_results = anime_provider.search_for_anime(
                    anime_title, config.translation_type
                )
            if not search_results:
                print("Search results not found")
                input("Enter to retry")
                search(config, anime_title, episode_range)
                return
            search_results = search_results["results"]
            if not search_results:
                print("Anime not found :cry:")
                exit_app()
            search_results_ = {
                search_result["title"]: search_result
                for search_result in search_results
            }

            if config.auto_select:
                search_result_manga_title = max(
                    search_results_.keys(),
                    key=lambda title: fuzz.ratio(
                        anime_normalizer.get(title, title), anime_title
                    ),
                )
                print("[cyan]Auto Selecting:[/] ", search_result_manga_title)

            else:
                choices = list(search_results_.keys())
                if config.use_fzf:
                    search_result_manga_title = fzf.run(
                        choices, "Please Select title", "FastAnime"
                    )
                elif config.use_rofi:
                    search_result_manga_title = Rofi.run(choices, "Please Select Title")
                else:
                    search_result_manga_title = fuzzy_inquirer(
                        choices,
                        "Please Select Title",
                    )

            # ---- fetch selected anime ----
            with Progress() as progress:
                progress.add_task("Fetching Anime...", total=None)
                anime: Anime | None = anime_provider.get_anime(
                    search_results_[search_result_manga_title]["id"]
                )

            if not anime:
                print("Sth went wring anime no found")
                input("Enter to continue...")
                search(config, anime_title, episode_range)
                return
            episodes_range = []
            episodes: list[str] = sorted(
                anime["availableEpisodesDetail"][config.translation_type], key=float
            )
            if episode_range:
                if ":" in episode_range:
                    ep_range_tuple = episode_range.split(":")
                    if len(ep_range_tuple) == 3 and all(ep_range_tuple):
                        episodes_start, episodes_end, step = ep_range_tuple
                        episodes_range = episodes[
                            int(episodes_start) : int(episodes_end) : int(step)
                        ]

                    elif len(ep_range_tuple) == 2 and all(ep_range_tuple):
                        episodes_start, episodes_end = ep_range_tuple
                        episodes_range = episodes[
                            int(episodes_start) : int(episodes_end)
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

                episodes_range = iter(episodes_range)

            if config.normalize_titles:
                from ...libs.common.mini_anilist import get_basic_anime_info_by_title

                anilist_anime_info = get_basic_anime_info_by_title(anime["title"])

            def stream_anime(anime: "Anime"):
                clear()
                episode = None

                if episodes_range:
                    try:
                        episode = next(episodes_range)  # pyright:ignore
                        print(
                            f"[cyan]Auto selecting:[/] {search_result_manga_title} [cyan]Episode:[/] {episode}"
                        )
                    except StopIteration:
                        print("[green]Completed binge sequence[/]:smile:")
                        return

                if not episode or episode not in episodes:
                    choices = [*episodes, "end"]
                    if config.use_fzf:
                        episode = fzf.run(
                            choices,
                            "Select an episode",
                            header=search_result_manga_title,
                        )
                    elif config.use_rofi:
                        episode = Rofi.run(choices, "Select an episode")
                    else:
                        episode = fuzzy_inquirer(
                            choices,
                            "Select episode",
                        )
                if episode == "end":
                    return

                # ---- fetch streams ----
                with Progress() as progress:
                    progress.add_task("Fetching Episode Streams...", total=None)
                    streams = anime_provider.get_episode_streams(
                        anime["id"], episode, config.translation_type
                    )
                    if not streams:
                        print("Failed to get streams")
                        return

                try:
                    # ---- fetch servers ----
                    if config.server == "top":
                        with Progress() as progress:
                            progress.add_task("Fetching top server...", total=None)
                            server = next(streams, None)
                            if not server:
                                print("Sth went wrong when fetching the episode")
                                input("Enter to continue")
                                stream_anime(anime)
                                return
                        stream_link = filter_by_quality(config.quality, server["links"])
                        if not stream_link:
                            print("Quality not found")
                            input("Enter to continue")
                            stream_anime(anime)
                            return
                        link = stream_link["link"]
                        subtitles = server["subtitles"]
                        stream_headers = server["headers"]
                        episode_title = server["episode_title"]
                    else:
                        with Progress() as progress:
                            progress.add_task("Fetching servers", total=None)
                            # prompt for server selection
                            servers = {server["server"]: server for server in streams}
                        servers_names = list(servers.keys())
                        if config.server in servers_names:
                            server = config.server
                        else:
                            if config.use_fzf:
                                server = fzf.run(servers_names, "Select an link")
                            elif config.use_rofi:
                                server = Rofi.run(servers_names, "Select an link")
                            else:
                                server = fuzzy_inquirer(
                                    servers_names,
                                    "Select link",
                                )
                        stream_link = filter_by_quality(
                            config.quality, servers[server]["links"]
                        )
                        if not stream_link:
                            print("Quality not found")
                            input("Enter to continue")
                            stream_anime(anime)
                            return
                        link = stream_link["link"]
                        stream_headers = servers[server]["headers"]
                        subtitles = servers[server]["subtitles"]
                        episode_title = servers[server]["episode_title"]

                    selected_anime_title = search_result_manga_title
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
                    print(
                        f"[purple]Now Playing:[/] {selected_anime_title} Episode {episode}"
                    )
                    subtitles = move_preferred_subtitle_lang_to_top(
                        subtitles, config.sub_lang
                    )
                    if config.sync_play:
                        from ..utils.syncplay import SyncPlayer

                        SyncPlayer(
                            link,
                            episode_title,
                            headers=stream_headers,
                            subtitles=subtitles,
                        )
                    else:
                        run_mpv(
                            link,
                            episode_title,
                            headers=stream_headers,
                            subtitles=subtitles,
                            player=config.player,
                        )
                except IndexError as e:
                    print(e)
                    input("Enter to continue")
                stream_anime(anime)

            stream_anime(anime)
