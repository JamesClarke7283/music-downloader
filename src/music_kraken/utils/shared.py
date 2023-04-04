from typing import List
import logging
import tempfile
import os
import configparser
from sys import platform as current_os
from pathlib import Path
import random

"""
I will now and then use those messages in the programm.
But I won't overuse them dw.

I will keep those messages, if you disagree with me on the messages,
feel free to fork the programm and edit them, or just edit them in the config
file once I implemented it.
"""
HAPPY_MESSAGES: List[str] = [
    "Support the artist.",
    "Star Me: https://github.com/HeIIow2/music-downloader",
    "🏳️‍⚧️🏳️‍⚧️ Trans rights are human rights. 🏳️‍⚧️🏳️‍⚧️",
    "🏳️‍⚧️🏳️‍⚧️ Trans women are women, trans men are men. 🏳️‍⚧️🏳️‍⚧️",
    "🏴‍☠️🏴‍☠️ Unite under one flag, fuck borders. 🏴‍☠️🏴‍☠️",
    "Join my Matrix Space: https://matrix.to/#/#music-kraken:matrix.org",
    "Gotta love BPJM!! :/"
]


def get_random_message() -> str:
    return random.choice(HAPPY_MESSAGES)


LOG_FILE = "download_logs.log"
TEMP_DIR = Path(tempfile.gettempdir(), "music-downloader")
TEMP_DIR.mkdir(exist_ok=True)

# configure logger default
logging.basicConfig(
    level=logging.INFO,
    format=logging.BASIC_FORMAT,
    handlers=[
        logging.FileHandler(os.path.join(TEMP_DIR, LOG_FILE)),
        logging.StreamHandler()
    ]
)

SONG_LOGGER = logging.getLogger("song-obj")
SEARCH_LOGGER = logging.getLogger("mb-cli")
INIT_PATH_LOGGER = logging.getLogger("init_path")
DATABASE_LOGGER = logging.getLogger("database")
METADATA_DOWNLOAD_LOGGER = logging.getLogger("metadata")
URL_DOWNLOAD_LOGGER = logging.getLogger("AudioSource")
TAGGING_LOGGER = logging.getLogger("tagging")
YOUTUBE_LOGGER = logging.getLogger("Youtube")
MUSIFY_LOGGER = logging.getLogger("Musify")
PATH_LOGGER = logging.getLogger("create-paths")
DOWNLOAD_LOGGER = logging.getLogger("download")
LYRICS_LOGGER = logging.getLogger("lyrics")
GENIUS_LOGGER = logging.getLogger("genius")
ENCYCLOPAEDIA_METALLUM_LOGGER = logging.getLogger("ma")

NOT_A_GENRE = ".", "..", "misc_scripts", "Music", "script", ".git", ".idea"
MUSIC_DIR = Path(os.path.expanduser("~"), "Music")

if current_os == "linux":
    # XDG_USER_DIRS_FILE reference: https://freedesktop.org/wiki/Software/xdg-user-dirs/
    XDG_USER_DIRS_FILE = os.path.join(os.path.expanduser("~"), ".config", "user-dirs.dirs")
    logger = logging.getLogger("init_path")
    logger.setLevel(logging.WARNING)
    try:
        with open(XDG_USER_DIRS_FILE, 'r') as f:
            data = "[XDG_USER_DIRS]\n" + f.read()
        config = configparser.ConfigParser(allow_no_value=True)
        config.read_string(data)
        xdg_config = config['XDG_USER_DIRS']
        MUSIC_DIR = os.path.expandvars(xdg_config['xdg_music_dir'].strip('"'))

    except (FileNotFoundError, KeyError) as E:
        logger.warning(
            f"Missing file or No entry found for \"xdg_music_dir\" in: \"{XDG_USER_DIRS_FILE}\".\n"
            f"Will fallback on default \"$HOME/Music\"."
        )

TOR = False
proxies = {
    'http': 'socks5h://127.0.0.1:9150',
    'https': 'socks5h://127.0.0.1:9150'
} if TOR else {}

"""
available variables:
- genre
- label
- artist
- album
- song
- album_type
"""
DOWNLOAD_PATH = "{genre}/{artist}/{album_type}/{album}"
DOWNLOAD_FILE = "{song}.mp3"
DEFAULT_VALUES = {
    "genre": "Various Genre",
    "label": "Various Labels",
    "artist": "Various Artists",
    "album": "Various Album",
    "song": "Various Song",
    "album_type": "Other"
}

# size of the chunks that are streamed
CHUNK_SIZE = 1024
# this is a percentage describing the percentage of failed downloads,
# relative to the total downloads.
# If the percentage goes over this threshold DownloadResult returns the download errors
# in the __str__ method
SHOW_DOWNLOAD_ERRORS_THRESHOLD = 0.3
