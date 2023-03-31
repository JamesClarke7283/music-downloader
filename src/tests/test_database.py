import sys
import os

# Add the parent directory of the src package to the Python module search path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from music_kraken.database import database
from music_kraken import objects

class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.db = database.Database("sqlite:///:memory:")
    
    def test_push(self):
        song = objects.Song(
            genre="HS Core",
            title="Vein Deep in the Solution",
            length=666,
            isrc="US-S1Z-99-00001",
            tracksort=2,
            target_list=[
                objects.Target(file="song.mp3", path="example")
            ],
            lyrics_list=[
                objects.Lyrics(
                    text="these are some depressive lyrics", language="en"),
                objects.Lyrics(
                    text="Dies sind depressive Lyrics", language="de")
            ],
            source_list=[
                objects.Source(objects.SourcePages.YOUTUBE,
                               "https://youtu.be/dfnsdajlhkjhsd"),
                objects.Source(objects.SourcePages.MUSIFY,
                               "https://ln.topdf.de/Music-Kraken/")
            ],
            album_list=[
                objects.Album(
                    title="One Final Action",
                    date=objects.ID3Timestamp(year=1986, month=3, day=1),
                    language=pycountry.languages.get(alpha_2="en"),
                    label_list=[
                        objects.Label(name="an album label")
                    ],
                    source_list=[
                        objects.Source(objects.SourcePages.ENCYCLOPAEDIA_METALLUM,
                                       "https://www.metal-archives.com/albums/I%27m_in_a_Coffin/One_Final_Action/207614")
                    ]
                ),
            ],
            main_artist_list=[
                objects.Artist(
                    name="I'm in a coffin",
                    source_list=[
                        objects.Source(
                            objects.SourcePages.ENCYCLOPAEDIA_METALLUM,
                            "https://www.metal-archives.com/bands/I%27m_in_a_Coffin/354")
                    ]
                )
            ]
        )
        self.db.push(song)
        self.assertEqual(self.db.pull(objects.Song, title="Vein Deep in the Solution"), song)

