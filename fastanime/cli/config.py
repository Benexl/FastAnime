import json
import logging
import os
import sys
import time
from configparser import ConfigParser
from typing import TYPE_CHECKING

from rich import print

from ..constants import (
    ASSETS_DIR,
    S_PLATFORM,
    USER_CONFIG_PATH,
    USER_DATA_PATH,
    USER_VIDEOS_DIR,
    USER_WATCH_HISTORY_PATH,
)
from ..libs.fzf import FZF_DEFAULT_OPTS, HEADER
from ..libs.rofi import Rofi

logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from ..AnimeProvider import AnimeProvider


class Config(object):
    manga = False
    sync_play = False
    anime_list: list
    watch_history: dict = {}
    fastanime_anilist_app_login_url = (
        "https://anilist.co/api/v2/oauth/authorize?client_id=20148&response_type=token"
    )
    anime_provider: "AnimeProvider"
    user_data = {
        "recent_anime": [],
        "animelist": [],
        "user": {},
        "meta": {"last_updated": 0},
    }
    default_config = {
        "auto_next": "False",
        "menu_order": "",
        "manga_viewer": "feh",
        "auto_select": "True",
        "cache_requests": "true",
        "check_for_updates": "True",
        "continue_from_history": "True",
        "default_media_list_tracking": "None",
        "downloads_dir": USER_VIDEOS_DIR,
        "disable_mpv_popen": "True",
        "discord": "False",
        "episode_complete_at": "80",
        "ffmpegthumbnailer_seek_time": "-1",
        "force_forward_tracking": "true",
        "force_window": "immediate",
        "fzf_opts": FZF_DEFAULT_OPTS,
        "header_color": "95,135,175",
        "header_ascii_art": HEADER,
        "format": "best[height<=1080]/bestvideo[height<=1080]+bestaudio/best",
        "icons": "false",
        "image_previews": "True" if S_PLATFORM != "win32" else "False",
        "image_renderer": "icat" if os.environ.get("KITTY_WINDOW_ID") else "chafa",
        "normalize_titles": "True",
        "notification_duration": "120",
        "max_cache_lifetime": "03:00:00",
        "mpv_args": "",
        "mpv_pre_args": "",
        "per_page": "15",
        "player": "mpv",
        "preferred_history": "local",
        "preferred_language": "english",
        "preview": "False",
        "preview_header_color": "215,0,95",
        "preview_separator_color": "208,208,208",
        "provider": "allanime",
        "quality": "1080",
        "recent": "50",
        "rofi_theme": os.path.join(ASSETS_DIR, "rofi_theme.rasi"),
        "rofi_theme_preview": os.path.join(ASSETS_DIR, "rofi_theme_preview.rasi"),
        "rofi_theme_confirm": os.path.join(ASSETS_DIR, "rofi_theme_confirm.rasi"),
        "rofi_theme_input": os.path.join(ASSETS_DIR, "rofi_theme_input.rasi"),
        "server": "top",
        "skip": "false",
        "sort_by": "search match",
        "sub_lang": "eng",
        "translation_type": "sub",
        "use_fzf": "False",
        "use_persistent_provider_store": "false",
        "use_python_mpv": "false",
        "use_rofi": "false",
    }

    def __init__(self, no_config) -> None:
        self.initialize_user_data_and_watch_history_recent_anime()
        self.load_config(no_config)

    def load_config(self, no_config=False):
        self.configparser = ConfigParser(self.default_config)
        self.configparser.add_section("stream")
        self.configparser.add_section("general")
        self.configparser.add_section("anilist")

        # --- set config values from file or using defaults ---
        try:
            if os.path.exists(USER_CONFIG_PATH) and not no_config:
                self.configparser.read(USER_CONFIG_PATH, encoding="utf-8")
        except Exception as e:
            print(
                "[yellow]Warning[/]: Failed to read config file using default configuration",
                file=sys.stderr,
            )
            logger.error(f"Failed to read config file: {e}")
            time.sleep(5)

        # get the configuration
        self.auto_next = self.configparser.getboolean("stream", "auto_next")
        self.auto_select = self.configparser.getboolean("stream", "auto_select")
        self.cache_requests = self.configparser.getboolean("general", "cache_requests")
        self.check_for_updates = self.configparser.getboolean(
            "general", "check_for_updates"
        )
        self.continue_from_history = self.configparser.getboolean(
            "stream", "continue_from_history"
        )
        self.default_media_list_tracking = self.configparser.get(
            "general", "default_media_list_tracking"
        )
        self.disable_mpv_popen = self.configparser.getboolean(
            "stream", "disable_mpv_popen"
        )
        self.discord = self.configparser.getboolean("general", "discord")
        self.downloads_dir = self.configparser.get("general", "downloads_dir")
        self.episode_complete_at = self.configparser.getint(
            "stream", "episode_complete_at"
        )
        self.ffmpegthumbnailer_seek_time = self.configparser.getint(
            "general", "ffmpegthumbnailer_seek_time"
        )
        self.force_forward_tracking = self.configparser.getboolean(
            "general", "force_forward_tracking"
        )
        self.force_window = self.configparser.get("stream", "force_window")
        self.format = self.configparser.get("stream", "format")
        self.fzf_opts = self.configparser.get("general", "fzf_opts")
        self.header_color = self.configparser.get("general", "header_color")
        self.header_ascii_art = self.configparser.get("general", "header_ascii_art")
        self.icons = self.configparser.getboolean("general", "icons")
        self.image_previews = self.configparser.getboolean("general", "image_previews")
        self.image_renderer = self.configparser.get("general", "image_renderer")
        self.normalize_titles = self.configparser.getboolean(
            "general", "normalize_titles"
        )
        self.notification_duration = self.configparser.getint(
            "general", "notification_duration"
        )
        self._max_cache_lifetime = self.configparser.get(
            "general", "max_cache_lifetime"
        )
        max_cache_lifetime = list(map(int, self._max_cache_lifetime.split(":")))
        self.max_cache_lifetime = (
            max_cache_lifetime[0] * 86400
            + max_cache_lifetime[1] * 3600
            + max_cache_lifetime[2] * 60
        )
        self.mpv_args = self.configparser.get("general", "mpv_args")
        self.mpv_pre_args = self.configparser.get("general", "mpv_pre_args")
        self.per_page = self.configparser.get("anilist", "per_page")
        self.player = self.configparser.get("stream", "player")
        self.preferred_history = self.configparser.get("stream", "preferred_history")
        self.preferred_language = self.configparser.get("general", "preferred_language")
        self.preview = self.configparser.getboolean("general", "preview")
        self.preview_separator_color = self.configparser.get(
            "general", "preview_separator_color"
        )
        self.preview_header_color = self.configparser.get(
            "general", "preview_header_color"
        )
        self.provider = self.configparser.get("general", "provider")
        self.quality = self.configparser.get("stream", "quality")
        self.recent = self.configparser.getint("general", "recent")
        self.rofi_theme_confirm = self.configparser.get("general", "rofi_theme_confirm")
        self.rofi_theme_input = self.configparser.get("general", "rofi_theme_input")
        self.rofi_theme = self.configparser.get("general", "rofi_theme")
        self.rofi_theme_preview = self.configparser.get("general", "rofi_theme_preview")
        self.server = self.configparser.get("stream", "server")
        self.skip = self.configparser.getboolean("stream", "skip")
        self.sort_by = self.configparser.get("anilist", "sort_by")
        self.menu_order = self.configparser.get("general", "menu_order")
        self.manga_viewer = self.configparser.get("general", "manga_viewer")
        self.sub_lang = self.configparser.get("general", "sub_lang")
        self.translation_type = self.configparser.get("stream", "translation_type")
        self.use_fzf = self.configparser.getboolean("general", "use_fzf")
        self.use_python_mpv = self.configparser.getboolean("stream", "use_python_mpv")
        self.use_rofi = self.configparser.getboolean("general", "use_rofi")
        self.use_persistent_provider_store = self.configparser.getboolean(
            "general", "use_persistent_provider_store"
        )

        Rofi.rofi_theme = self.rofi_theme
        Rofi.rofi_theme_input = self.rofi_theme_input
        Rofi.rofi_theme_confirm = self.rofi_theme_confirm
        Rofi.rofi_theme_preview = self.rofi_theme_preview

        os.environ["FZF_DEFAULT_OPTS"] = self.fzf_opts

        # ---- setup user data ------
        self.anime_list: list = self.user_data.get("animelist", [])
        self.user: dict = self.user_data.get("user", {})

        if not os.path.exists(USER_CONFIG_PATH):
            with open(USER_CONFIG_PATH, "w", encoding="utf-8") as config:
                config.write(self.__repr__())

    def set_fastanime_config_environs(self):
        current_config = []
        for key in self.default_config:
            if not os.environ.get(f"FASTANIME_{key.upper()}"):
                current_config.append(
                    (f"FASTANIME_{key.upper()}", str(getattr(self, key)))
                )
        os.environ.update(current_config)

    def update_user(self, user):
        self.user = user
        self.user_data["user"] = user
        self._update_user_data()

    def update_recent(self, recent_anime: list):
        recent_anime_ids = []
        _recent_anime = []
        for anime in recent_anime:
            if (
                anime["id"] not in recent_anime_ids
                and len(recent_anime_ids) <= self.recent
            ):
                _recent_anime.append(anime)
                recent_anime_ids.append(anime["id"])

        self.user_data["recent_anime"] = _recent_anime
        self._update_user_data()

    def media_list_track(
        self,
        anime_id: int,
        episode_no: str,
        episode_stopped_at="0",
        episode_total_length="0",
        progress_tracking="prompt",
    ):
        self.watch_history.update(
            {
                str(anime_id): {
                    "episode_no": episode_no,
                    "episode_stopped_at": episode_stopped_at,
                    "episode_total_length": episode_total_length,
                    "progress_tracking": progress_tracking,
                }
            }
        )
        with open(USER_WATCH_HISTORY_PATH, "w") as f:
            json.dump(self.watch_history, f)

    def initialize_user_data_and_watch_history_recent_anime(self):
        try:
            if os.path.isfile(USER_DATA_PATH):
                with open(USER_DATA_PATH, "r") as f:
                    user_data = json.load(f)
                    self.user_data.update(user_data)
        except Exception as e:
            logger.error(e)
        try:
            if os.path.isfile(USER_WATCH_HISTORY_PATH):
                with open(USER_WATCH_HISTORY_PATH, "r") as f:
                    watch_history = json.load(f)
                    self.watch_history.update(watch_history)
        except Exception as e:
            logger.error(e)

    def _update_user_data(self):
        """method that updates the actual user data file"""
        with open(USER_DATA_PATH, "w") as f:
            json.dump(self.user_data, f)

    def update_config(self, section: str, key: str, value: str):
        self.configparser.set(section, key, value)
        with open(USER_CONFIG_PATH, "w") as config:
            self.configparser.write(config)

    def __repr__(self):
        new_line = "\n"
        tab = "\t"
        current_config_state = f"""\
#
#    ███████╗░█████╗░░██████╗████████╗░█████╗░███╗░░██╗██╗███╗░░░███╗███████╗  ░█████╗░░█████╗░███╗░░██╗███████╗██╗░██████╗░
#    ██╔════╝██╔══██╗██╔════╝╚══██╔══╝██╔══██╗████╗░██║██║████╗░████║██╔════╝  ██╔══██╗██╔══██╗████╗░██║██╔════╝██║██╔════╝░
#    █████╗░░███████║╚█████╗░░░░██║░░░███████║██╔██╗██║██║██╔████╔██║█████╗░░  ██║░░╚═╝██║░░██║██╔██╗██║█████╗░░██║██║░░██╗░
#    ██╔══╝░░██╔══██║░╚═══██╗░░░██║░░░██╔══██║██║╚████║██║██║╚██╔╝██║██╔══╝░░  ██║░░██╗██║░░██║██║╚████║██╔══╝░░██║██║░░╚██╗
#    ██║░░░░░██║░░██║██████╔╝░░░██║░░░██║░░██║██║░╚███║██║██║░╚═╝░██║███████╗  ╚█████╔╝╚█████╔╝██║░╚███║██║░░░░░██║╚██████╔╝
#    ╚═╝░░░░░╚═╝░░╚═╝╚═════╝░░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚══╝╚═╝╚═╝░░░░░╚═╝╚══════╝  ░╚════╝░░╚════╝░╚═╝░░╚══╝╚═╝░░░░░╚═╝░╚═════╝░
#
[general]
# Can you rice it?
# For the preview pane
preview_separator_color = {self.preview_separator_color}

preview_header_color = {self.preview_header_color}

# For the header 
# Be sure to indent
header_ascii_art = {new_line.join([tab + line for line in self.header_ascii_art.split(new_line)])}

header_color = {self.header_color}

# the image renderer to use [icat/chafa]
image_renderer = {self.image_renderer}
 
# To be passed to fzf
# Be sure to indent
fzf_opts = {new_line.join([tab + line for line in self.fzf_opts.split(new_line)])}

# Whether to show the icons in the TUI [True/False]
# More like emojis
# By the way, if you have any recommendations
# for which should be used where, please
# don't hesitate to share your opinion
# because it's a lot of work
# to look for the right one for each menu option
# Be sure to also give the replacement emoji
icons = {self.icons}

# Whether to normalize provider titles [True/False]
# Basically takes the provider titles and finds the corresponding Anilist title, then changes the title to that
# Useful for uniformity, especially when downloading from different providers
# This also applies to episode titles
normalize_titles = {self.normalize_titles}

# Whether to check for updates every time you run the script [True/False]
# This is useful for keeping your script up to date
# because there are always new features being added 😄
check_for_updates = {self.check_for_updates}

# Can be [allanime, animepahe, hianime, nyaa, yugen]
# Allanime is the most reliable
# Animepahe provides different links to streams of different quality, so a quality can be selected reliably with the --quality option
# Hianime usually provides subs in different languages, and its servers are generally faster
# NOTE: Currently, they are encrypting the video links
# though I’m working on it
# However, you can still get the links to the subs
# with ```fastanime grab``` command
# Yugen meh
# Nyaa for those who prefer torrents, though not reliable due to auto-selection of results
# as most of the data in Nyaa is not structured
# though it works relatively well for new anime
# especially with SubsPlease and HorribleSubs
# Oh, and you should have webtorrent CLI to use this
provider = {self.provider}

# Display language [english, romaji]
# This is passed to Anilist directly and is used to set the language for anime titles
# when using the Anilist interface
preferred_language = {self.preferred_language}

# Download directory
# Where you will find your videos after downloading them with 'fastanime download' command
downloads_dir = {self.downloads_dir}

# Whether to show a preview window when using fzf or rofi [True/False]
# The preview requires you to have a command-line image viewer as documented in the README
# This is only when using fzf or rofi
# If you don't care about image and text previews, it doesn’t matter
# though it’s awesome
# Try it, and you will see
preview = {self.preview} 

# Whether to show images in the preview [True/False]
# Windows users: just switch to Linux 😄
# because even if you enable it 
# it won't look pretty
# Just be satisfied with the text previews
# So forget it exists 🤣
image_previews = {self.image_previews}

# the time to seek when using ffmpegthumbnailer [-1 to 100]
# -1 means random and is the default
# ffmpegthumbnailer is used to generate previews,
# allowing you to select the time in the video to extract an image.
# Random makes things quite exciting because you never know at what time it will extract the image.
# Used by the `fastanime downloads` command.
ffmpegthumbnailer_seek_time = {self.ffmpegthumbnailer_seek_time}

# specify the order of menu items in a comma-separated list.
# Only include the base names of menu options (e.g., "Trending", "Recent").
# The default value is 'Trending,Recent,Watching,Paused,Dropped,Planned,Completed,Rewatching,Recently Updated Anime,Search,Watch History,Random Anime,Most Popular Anime,Most Favourite Anime,Most Scored Anime,Upcoming Anime,Edit Config,Exit'.
# Leave blank to use the default menu order.
# You can also omit some options by not including them in the list.
menu_order = {self.menu_order}

# whether to use fzf as the interface for the anilist command and others. [True/False]
use_fzf = {self.use_fzf} 

# whether to use rofi for the UI [True/False]
# It's more useful if you want to create a desktop entry, 
# which can be set up with 'fastanime config --desktop-entry'.
# If you want it to be your sole interface even when fastanime is run directly from the terminal, enable this.
use_rofi = {self.use_rofi}

# rofi themes to use <path>
# The value of this option is the path to the rofi config files to use.
# I chose to split it into 4 since it gives the best look and feel.
# You can refer to the rofi demo on GitHub to see for yourself.
# I need help designing the default rofi themes.
# If you fancy yourself a rofi ricer, please contribute to improving 
# the default theme.
rofi_theme = {self.rofi_theme}

rofi_theme_preview = {self.rofi_theme_preview}

rofi_theme_input = {self.rofi_theme_input}

rofi_theme_confirm = {self.rofi_theme_confirm}

# the duration in minutes a notification will stay on the screen.
# Used by the notifier command.
notification_duration = {self.notification_duration}

# used when the provider offers subtitles in different languages.
# Currently, this is the case for:
# hianime.
# The values for this option are the short names for languages.
# Regex is used to determine what you selected.
sub_lang = {self.sub_lang}

# what is your default media list tracking [track/disabled/prompt]
# This only affects your anilist anime list.
# track - means your progress will always be reflected in your anilist anime list.
# disabled - means progress tracking will no longer be reflected in your anime list.
# prompt - means you will be prompted for each anime whether you want your progress to be tracked or not.
default_media_list_tracking = {self.default_media_list_tracking}

# whether media list tracking should only be updated when the next episode is greater than the previous.
# This only affects your anilist anime list.
force_forward_tracking = {self.force_forward_tracking}

# whether to cache requests [true/false]
# This improves the experience by making it faster, 
# as data doesn't always need to be fetched from the web server 
# and can instead be retrieved locally from the cached_requests_db.
cache_requests = {self.cache_requests}

# the max lifetime for a cached request <days:hours:minutes>
# Defaults to 3 days = 03:00:00.
# This is the time after which a cached request will be deleted (technically).
max_cache_lifetime = {self._max_cache_lifetime}

# whether to use a persistent store (basically an SQLite DB) for storing some data the provider requires
# to enable a seamless experience. [true/false]
# This option exists primarily to optimize FastAnime as a library in a website project.
# For now, it's not recommended to change it. Leave it as is.
use_persistent_provider_store = {self.use_persistent_provider_store}

# number of recent anime to keep [0-50].
# 0 will disable recent anime tracking.
recent = {self.recent}

# enable or disable Discord activity updater.
# If you want to enable it, please follow the link below to register the app with your Discord account:
# https://discord.com/oauth2/authorize?client_id=1292070065583165512
discord = {self.discord}

# comma separated list of args that will be passed to mpv
# example: --vo=kitty,--fullscreen,--volume=50
mpv_args = {self.mpv_args}

# command line options passed before the mpv command
# example: kitty
# useful incase of wanting to run sth like: kitty mpv --vo=kitty <url>
mpv_pre_args = {self.mpv_pre_args}

# choose manga viewer [feh/icat]
# feh is the default and requires feh to be installed
# icat is for kitty terminal users only
manga_viewer = {self.manga_viewer}

[stream]
# the quality of the stream [1080,720,480,360]
# this option is usually only reliable when:
# provider=animepahe
# since it provides links that actually point to streams of different qualities
# while the rest just point to another link that can provide the anime from the same server
quality = {self.quality}

# Auto continue from watch history [True/False]
# this will make fastanime to choose the episode that you last watched to completion
# and increment it by one
# and use that to auto select the episode you want to watch
continue_from_history = {self.continue_from_history}  

# which history to use [local/remote]
# local history means it will just use the watch history stored locally in your device 
# the file that stores it is called watch_history.json
# and is stored next to your config file
# remote means it ignores the last episode stored locally
# and instead uses the one in your anilist anime list
# this config option is useful if you want to overwrite your local history
# or import history covered from another device or platform
# since remote history will take precendence over whats available locally
preferred_history = {self.preferred_history}

# Preferred language for anime [dub/sub]
translation_type = {self.translation_type}

# what server to use for a particular provider
# allanime: [dropbox, sharepoint, wetransfer, gogoanime, wixmp]
# animepahe: [kwik]
# hianime: [HD1, HD2, StreamSB, StreamTape] : only HD2 for now
# yugen: [gogoanime]
# 'top' can also be used as a value for this option
# 'top' will cause fastanime to auto select the first server it sees
# this saves on resources and is faster since not all servers are being fetched
server = {self.server}

# Auto select next episode [True/False]
# this makes fastanime increment the current episode number 
# then after using that value to fetch the next episode instead of prompting
# this option is useful for binging
auto_next = {self.auto_next}

# Auto select the anime provider results with fuzzy find. [True/False]
# Note this won't always be correct
# this is because the providers sometime use non-standard names
# that are there own preference rather than the official names
# But 99% of the time will be accurate
# if this happens just turn off auto_select in the menus or from the commandline 
# and manually select the correct anime title
# edit this file <https://github.com/Benexl/FastAnime/blob/master/fastanime/Utility/data.py>
# and to the dictionary of the provider
# the provider title (key) and their corresponding anilist names (value)
# and then please open a pr 
# issues on the same will be ignored and then closed 😆
auto_select = {self.auto_select}

# whether to skip the opening and ending theme songs [True/False]
# NOTE: requires ani-skip to be in path
# for python-mpv users am planning to create this functionality n python without the use of an external script
# so its disabled for now
# and anyways Dan Da Dan
# taught as the importance of letting it flow 🙃
skip = {self.skip}

# at what percentage progress should the episode be considered as completed [0-100]
# this value is used to determine whether to increment the current episode number and save it to your local list
# so you can continue immediately to the next episode without select it the next time you decide to watch the anime
# it is also used to determine whether your anilist anime list should be updated or not
episode_complete_at = {self.episode_complete_at}

# whether to use python-mpv [True/False]
# to enable superior control over the player 
# adding more options to it
# Enabling this option and you will ask yourself
# why you did not discover fastanime sooner 🙃
# Since you basically don't have to close the player window 
# to go to the next or previous episode, switch servers, 
# change translation type or change to a given episode x
# so try it if you haven't already
# if you have any issues setting it up 
# don't be afraid to ask
# especially on windows
# honestly it can be a pain to set it up there
# personally it took me quite sometime to figure it out
# this is because of how windows handles shared libraries
# so just ask when you find yourself stuck
# or just switch to nixos 😄
use_python_mpv = {self.use_python_mpv}


# whether to use popen to get the timestamps for continue_from_history
# implemented because popen does not work for some reason in nixos and apparently on mac as well
# if you are on nixos or mac and you have a solution to this problem please share
# i will be glad to hear it 😄
# So for now ignore this option
# and anyways the new method of getting timestamps is better
disable_mpv_popen = {self.disable_mpv_popen}

# force mpv window
# the default 'immediate' just makes mpv to open the window even if the video has not yet loaded
# done for asthetics
# passed directly to mpv so values are same
force_window = immediate

# the format of downloaded anime and trailer
# based on yt-dlp format and passed directly to it
# learn more by looking it up on their site
# only works for downloaded anime if: 
# provider=allanime, server=gogoanime
# provider=allanime, server=wixmp
# provider=hianime
# this is because they provider a m3u8 file that contans multiple quality streams
format = {self.format}

# set the player to use for streaming [mpv/vlc]
# while this option exists i will still recommend that you use mpv
# since you will miss out on some features if you use the others
player = {self.player}

[anilist]
per_page = {self.per_page}

#
# HOPE YOU ENJOY FASTANIME AND BE SURE TO STAR THE PROJECT ON GITHUB
# https://github.com/Benexl/FastAnime
#
# Also join the discord server
# where the anime tech community lives :)
# https://discord.gg/C4rhMA4mmK
#
"""
        return current_config_state

    def __str__(self):
        return self.__repr__()
