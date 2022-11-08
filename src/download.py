import mutagen.id3
import requests
import os.path
from mutagen.easyid3 import EasyID3
from pydub import AudioSegment
import logging

from scraping import musify, youtube_music

"""
https://en.wikipedia.org/wiki/ID3
https://mutagen.readthedocs.io/en/latest/user/id3.html

# to get all valid keys
from mutagen.easyid3 import EasyID3
print("\n".join(EasyID3.valid_keys.keys()))
print(EasyID3.valid_keys.keys())
"""


class Download:
    def __init__(self, database, logger: logging.Logger, proxies: dict = None, base_path: str = ""):
        if proxies is not None:
            musify.set_proxy(proxies)

        self.database = database
        self.logger = logger

        for row in database.get_tracks_to_download():
            row['artist'] = [i['name'] for i in row['artists']]
            row['file'] = os.path.join(base_path, row['file'])
            row['path'] = os.path.join(base_path, row['path'])

            if self.path_stuff(row['path'], row['file']):
                self.write_metadata(row, row['file'])
                continue

            download_success = None
            src = row['src']
            if src == 'musify':
                download_success = musify.download(row)
            elif src == 'youtube':
                download_success = youtube_music.download(row)

            if download_success == -1:
                self.logger.warning(f"couldn't download {row['url']} from {row['src']}")
                continue

            self.write_metadata(row, row['file'])

    def write_metadata(self, row, file_path):
        if not os.path.exists(file_path):
            self.logger.warning("something went really wrong")
            return False

        # only convert the file to the proper format if mutagen doesn't work with it due to time
        try:
            audiofile = EasyID3(file_path)
        except mutagen.id3.ID3NoHeaderError:
            AudioSegment.from_file(file_path).export(file_path, format="mp3")
            audiofile = EasyID3(file_path)

        valid_keys = list(EasyID3.valid_keys.keys())

        for key in list(row.keys()):
            if key in valid_keys and row[key] is not None:
                if type(row[key]) != list:
                    row[key] = str(row[key])
                audiofile[key] = row[key]

        self.logger.info("saving")
        audiofile.save(file_path, v1=2)

    def path_stuff(self, path: str, file_: str):
        # returns true if it shouldn't be downloaded
        if os.path.exists(file_):
            self.logger.info(f"'{file_}' does already exist, thus not downloading.")
            return True
        os.makedirs(path, exist_ok=True)
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    s = requests.Session()
    Download(session=s, base_path=os.path.expanduser('~/Music'))
