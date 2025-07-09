import logging
import os
import shutil
import subprocess
import tempfile
from queue import Queue
from threading import Thread

import yt_dlp
from rich import print
from rich.prompt import Confirm
from yt_dlp.utils import sanitize_filename

logger = logging.getLogger(__name__)


class YtDLPDownloader:
    downloads_queue = Queue()
    _thread = None

    def _worker(self):
        while True:
            task, args = self.downloads_queue.get()
            try:
                task(*args)
            except Exception as e:
                logger.error(f"Something went wrong {e}")
            self.downloads_queue.task_done()

    def _download_file(
        self,
        url: str,
        anime_title: str,
        episode_title: str,
        download_dir: str,
        silent: bool,
        progress_hooks=[],
        vid_format: str = "best",
        force_unknown_ext=False,
        verbose=False,
        headers={},
        sub="",
        merge=False,
        clean=False,
        prompt=True,
        force_ffmpeg=False,
        hls_use_mpegts=False,
        hls_use_h264=False,
        nocheckcertificate=False,
    ):
        """Helper function that downloads anime given url and path details

        Args:
            url: [TODO:description]
            anime_title: [TODO:description]
            episode_title: [TODO:description]
            download_dir: [TODO:description]
            silent: [TODO:description]
            vid_format: [TODO:description]
        """
        anime_title = sanitize_filename(anime_title)
        episode_title = sanitize_filename(episode_title)
        if url.endswith(".torrent"):
            WEBTORRENT_CLI = shutil.which("webtorrent")
            if not WEBTORRENT_CLI:
                import time

                print(
                    "webtorrent cli is not installed which is required for downloading and streaming from nyaa\nplease install it or use another provider"
                )
                time.sleep(120)
                return
            cmd = [
                WEBTORRENT_CLI,
                "download",
                url,
                "--out",
                os.path.join(download_dir, anime_title, episode_title),
            ]
            subprocess.run(cmd)
            return
        ydl_opts = {
            # Specify the output path and template
            "http_headers": headers,
            "outtmpl": f"{download_dir}/{anime_title}/{episode_title}.%(ext)s",
            "silent": silent,
            "verbose": verbose,
            "format": vid_format,
            "compat_opts": ("allow-unsafe-ext",) if force_unknown_ext else tuple(),
            "progress_hooks": progress_hooks,
            "nocheckcertificate": nocheckcertificate,
        }
        urls = [url]
        if sub:
            urls.append(sub)
        vid_path = ""
        sub_path = ""
        for i, url in enumerate(urls):
            options = ydl_opts
            if i == 0:
                if force_ffmpeg:
                    options = options | {
                        "external_downloader": {"default": "ffmpeg"},
                        "external_downloader_args": {
                            "ffmpeg_i1": ["-v", "error", "-stats"],
                        },
                    }
                if hls_use_mpegts:
                    options = options | {
                        "hls_use_mpegts": True,
                        "outtmpl": ".".join(options["outtmpl"].split(".")[:-1]) + ".ts", # force .ts extension
                    }
                elif hls_use_h264:
                    options = options | {
                        "external_downloader_args": options["external_downloader_args"] | {
                            "ffmpeg_o1": [
                                "-c:v", "copy",
                                "-c:a", "aac",
                                "-bsf:a", "aac_adtstoasc",
                                "-q:a", "1",
                                "-ac", "2",
                                "-af", "loudnorm=I=-22:TP=-2.5:LRA=11,alimiter=limit=-1.5dB", # prevent clipping from HE-AAC to AAC convertion
                            ],
                        }
                    }

            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=True)
            if not info:
                continue
            if i == 0:
                vid_path: str = info["requested_downloads"][0]["filepath"]
                if vid_path.endswith(".unknown_video"):
                    print("Normalizing path...")
                    _vid_path = vid_path.replace(".unknown_video", ".mp4")
                    shutil.move(vid_path, _vid_path)
                    vid_path = _vid_path
                    print("successfully normalized path")

            else:
                sub_path = info["requested_downloads"][0]["filepath"]
        if sub_path and vid_path and merge:
            self.merge_subtitles(vid_path, sub_path, clean, prompt)

    def merge_subtitles(self, video_path, sub_path, clean, prompt):
        # Extract the directory and filename
        video_dir = os.path.dirname(video_path)
        video_name = os.path.basename(video_path)
        video_name, _ = os.path.splitext(video_name)
        video_name += ".mkv"

        FFMPEG_EXECUTABLE = shutil.which("ffmpeg")
        if not FFMPEG_EXECUTABLE:
            print("[yellow bold]WARNING: [/]FFmpeg not found")
            return
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Temporary output path in the temporary directory
            temp_output_path = os.path.join(temp_dir, video_name)
            # FFmpeg command to merge subtitles
            command = [
                FFMPEG_EXECUTABLE,
                "-hide_banner",
                "-i",
                video_path,
                "-i",
                sub_path,
                "-c",
                "copy",
                "-map",
                "0",
                "-map",
                "1",
                temp_output_path,
            ]

            # Run the command
            try:
                subprocess.run(command, check=True)

                # Move the file back to the original directory with the original name
                final_output_path = os.path.join(video_dir, video_name)

                if os.path.exists(final_output_path):
                    if not prompt or Confirm.ask(
                        f"File exists({final_output_path}) would you like to overwrite it",
                        default=True,
                    ):
                        # move file to dest
                        os.remove(final_output_path)
                        shutil.move(temp_output_path, final_output_path)
                else:
                    shutil.move(temp_output_path, final_output_path)
                # clean up
                if clean:
                    print("[cyan]Cleaning original files...[/]")
                    os.remove(video_path)
                    os.remove(sub_path)

                print(
                    f"[green bold]Subtitles merged successfully.[/] Output file: {final_output_path}"
                )
            except subprocess.CalledProcessError as e:
                print(f"[red bold]Error[/] during merging subtitles: {e}")
            except Exception as e:
                print(f"[red bold]An error[/] occurred: {e}")

    def download_file(
        self,
        url: str,
        anime_title: str,
        episode_title: str,
        download_dir: str,
        silent: bool = True,
        **kwargs,
    ):
        """A helper that just does things in the background

        Args:
            title ([TODO:parameter]): [TODO:description]
            silent ([TODO:parameter]): [TODO:description]
            url: [TODO:description]
        """
        if not self._thread:
            self._thread = Thread(target=self._worker)
            self._thread.daemon = True
            self._thread.start()

        self.downloads_queue.put(
            (
                self._download_file,
                (url, anime_title, episode_title, download_dir, silent),
            )
        )


downloader = YtDLPDownloader()
