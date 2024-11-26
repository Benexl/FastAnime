import json
import logging
import os
from configparser import ConfigParser
from typing import TYPE_CHECKING
from ..libs.fzf import FZF_DEFAULT_OPTS, HEADER

from ..constants import (
    USER_CONFIG_PATH,
    USER_DATA_PATH,
    USER_VIDEOS_DIR,
    ASSETS_DIR,
    USER_WATCH_HISTORY_PATH,
    S_PLATFORM,
)
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
    user_data = {"recent_anime": [], "animelist": [], "user": {}}
    default_config = {
        "auto_next": "False",
        "auto_select": "True",
        "cache_requests": "true",
        "check_for_updates": "True",
        "continue_from_history": "True",
        "default_media_list_tracking": "None",
        "downloads_dir": USER_VIDEOS_DIR,
        "discord": "False",
        "disable_mpv_popen": "True",
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
        "normalize_titles": "True",
        "notification_duration": "2",
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

    def __init__(self) -> None:
        self.initialize_user_data_and_watch_history_recent_anime()
        self.load_config()

    def load_config(self):
        self.configparser = ConfigParser(self.default_config)
        self.configparser.add_section("stream")
        self.configparser.add_section("general")
        self.configparser.add_section("anilist")

        # --- set config values from file or using defaults ---
        if os.path.exists(USER_CONFIG_PATH):
            self.configparser.read(USER_CONFIG_PATH, encoding="utf-8")

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
        self.discord = self.configparser.getboolean(
            "general", "discord"
        )
        self.disable_mpv_popen = self.configparser.getboolean(
            "stream", "disable_mpv_popen"
        )
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
        self.normalize_titles = self.configparser.getboolean(
            "general", "normalize_titles"
        )
        self.notification_duration = self.configparser.getint(
            "general", "notification_duration"
        )
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
            current_config.append((f"FASTANIME_{key.upper()}", str(getattr(self, key))))
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
# well recently somebody made a post @unixporn subreddit
# the rice contained fastanime in preview mode
# Did not even realise you rice with it
# or i would have cross-posted
# 'A new way to rice'
# and immediately one of the mods removed it
# am not sure why though
# cause the preview is actually pretty good looking.
# just like you would use fastfetch or cava
# as means to protest against this injustice i have addded
# the following
# for you all ricers out there
# and be sure to post a rice with fastanime on it
# if you also think this is unfair

# for the preview pane
preview_separator_color = {self.preview_separator_color}

preview_header_color = {self.preview_header_color}

# for the header 
# be sure to indent
header_ascii_art = {new_line.join([tab+line for line in self.header_ascii_art.split(new_line)])}

header_color = {self.header_color}

# to be passed to fzf
# may break it down further for now just pass the options as is
# be sure to indent
fzf_opts = {new_line.join([tab+line for line in self.fzf_opts.split(new_line)])}

# whether to show the icons in the tui [True/False]
# more like emojis
# by the way if you have any recommendations
# to which should be used where please
# don't hesitate to share your opinion
# cause it's a lot of work
# to look for the right one for each menu option
# be sure to also give the replacement emoji
icons = {self.icons}

# whether to normalize provider titles [True/False]
# basically takes the provider titles and finds the corresponding anilist title then changes the title to that
# useful for uniformity especially when downloading from different providers
# this also applies to episode titles
normalize_titles = {self.normalize_titles}

# whether to check for updates every time you run the script [True/False]
# this is useful for keeping your script up to date
# cause there are always new features being added 😄
check_for_updates = {self.check_for_updates}

# can be [allanime, animepahe, hianime, nyaa, yugen]
# allanime is the most realible
# animepahe provides different links to streams of different quality so a quality can be selected reliably with --quality option
# hianime usually provides subs in different languuages and its servers are generally faster
# NOTE: currently they are encrypting the video links 
# though am working on it
# however, you can still get the links to the subs
# with ```fastanime grab``` command
# yugen meh
# nyaa those who prefer torrents, though not reliable due to auto selection of results
# as most of the data in nyaa is not structured
# though works relatively well for new anime
# esp with subsplease and horriblesubs
# oh and you should have webtorrent cli to use this
provider = {self.provider}

# Display language [english, romaji]
# this is passed to anilist directly and is used to set the language which the anime titles will be in
# when using the anilist interface
preferred_language = {self.preferred_language}

# Download directory
# where you will find your videos after downloading them with 'fastanime download' command
downloads_dir = {self.downloads_dir}

# whether to show a preview window when using fzf or rofi [True/False]
# the preview requires you have a commandline image viewer as documented in the README
# this is only when usinf fzf
# if you dont care about image previews it doesnt matter
# though its awesome
# try it and you will see
preview = {self.preview} 

# whether to show images in the preview [true/false]
# windows users just swtich to linux 😄
# cause even if you enable it 
# it won't look pretty
# just be satisfied with the text previews
# so forget it exists 🤣
image_previews = {self.image_previews}

# the time to seek when using ffmpegthumbnailer [-1 to 100]
# -1 means random and is the default
# ffmpegthumbnailer is used to generate previews and you can select at what time in the video to extract an image
# random makes things quite exciting cause you never no at what time it will extract the image from
ffmpegthumbnailer_seek_time = {self.ffmpegthumbnailer_seek_time}

# whether to use fzf as the interface for the anilist command and others. [True/False]
use_fzf = {self.use_fzf} 

# whether to use rofi for the ui [True/False]
# it's more useful if you want to create a desktop entry 
# which can be setup with 'fastanime config --desktop-entry'
# though if you want it to be your sole interface even when fastanime is run directly from the terminal
use_rofi = {self.use_rofi}

# rofi themes to use <path>
# the values of this option is the path to the rofi config files to use
# i choose to split it into 4 since it gives the best look and feel
# you can refer to the rofi demo on github to see for your self
# i need help designing the default rofi themes
# if you fancy yourself a rofi ricer please contribute to making 
# the default theme better
rofi_theme = {self.rofi_theme}

rofi_theme_preview = {self.rofi_theme_preview}

rofi_theme_input = {self.rofi_theme_input}

rofi_theme_confirm = {self.rofi_theme_confirm}

# the duration in minutes a notification will stay in the screen
# used by notifier command
notification_duration = {self.notification_duration}

# used when the provider gives subs of different languages
# currently its the case for:
# hianime
# the values for this option are the short names for languages
# regex is used to determine what you selected
sub_lang = {self.sub_lang}

# what is your default media list tracking [track/disabled/prompt]
# only affects your anilist anime list
# track - means your progress will always be reflected in your anilist anime list
# disabled - means progress tracking will no longer be reflected in your anime list
# prompt - means for every anime you will be prompted whether you want your progress to be tracked or not
default_media_list_tracking = {self.default_media_list_tracking}

# whether media list tracking should only be updated when the next episode is greater than the previous
# this affects only your anilist anime list
force_forward_tracking = {self.force_forward_tracking}

# whether to cache requests [true/false]
# this makes the experience better and more faster
# as data need not always be fetched from web server
# and instead can be gotten  locally
# from the cached_requests_db
cache_requests = {self.cache_requests}

# whether to use a persistent store (basically a sqlitedb) for storing some data the provider requires
# to enable a seamless experience [true/false]
# this option exists primarily because i think it may help in the optimization
# of fastanime as a library in a website project
# for now i don't recommend changing it
# leave it as is
use_persistent_provider_store = {self.use_persistent_provider_store}

# no of recent anime to keep [0-50]
# 0 will disable recent anime tracking
recent = {self.recent}

# enable or disable discord activity updater
# if you want to enable it, please follow the lnik below to register the app with discord account
# https://discord.com/oauth2/authorize?client_id=1310622369022476428
discord = {self.discord}

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
# the file that stores it is called watch_history.json and is stored next to your config file
# remote means it ignores the last episode stored locally and instead uses the one in your anilist anime list
# this config option is useful if you want to overwrite your local history or import history covered from another device or platform
# since remote history will take precendence over whats available locally
preferred_history = {self.preferred_history}

# Preferred language for anime [dub/sub]
translation_type = {self.translation_type}

# what server to use for a particular provider
# allanime: [dropbox, sharepoint, wetransfer, gogoanime, wixmp]
# animepahe: [kwik]
# hianime: [HD1, HD2, StreamSB, StreamTape]
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
# if this happens just turn of auto_select in the menus or from the commandline and manually select the correct anime title
# and then please open an issue 
# highlighting the normalized title 
# and the title given by the provider for the anime you wished to watch  
# or even better edit this file <https://github.com/Benex254/FastAnime/blob/master/fastanime/Utility/data.py>
# and open a pull request 
# prefrably, so you can give me a small break
# of doing everything 😄
# and its always nice to see people contributing
# to projects they love and use
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
# Enable this one and you will be wonder 
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
# or just switch to arch linux
use_python_mpv = {self.use_python_mpv}


# whether to use popen to get the timestamps for continue_from_history
# implemented because popen does not work for some reason in nixos
# if you are on nixos and you have a solution to this problem please share
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

# NOTE:
# if you have any trouble setting up your config
# please don't be afraid to ask in our discord
# plus if there are any errors, improvements or suggestions please tell us in the discord
# or help us by contributing
# we appreciate all the help we can get
# since we may not always have the time to immediately implement the changes
#
# HOPE YOU ENJOY FASTANIME AND BE SURE TO STAR THE PROJECT ON GITHUB
# https://github.com/Benex254/FastAnime
# 
"""
        return current_config_state

    def __str__(self):
        return self.__repr__()
