from typing import Union
from sqlalchemy import Column, Integer, Boolean, String, Text, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

from ..objects import FormattedText, ID3Timestamp

"""
**IMPORTANT**:

never delete, modify the datatype or add constrains to ANY existing collumns,
between the versions, that gets pushed out to the users.
Else my function can't update legacy databases, to new databases, 
while keeping the data of the old ones.

EVEN if that means to for example keep decimal values stored in strings.
(not in my codebase though.)
"""

class Base(declarative_base()):
    id: int = Column(Integer(), primary_key=True)

class Song(Base):
    """A class representing a song in the music database."""
    __tablename__ = "songs"

    title: str = Column(String(), nullable=True)
    isrc: str = Column(String(), nullable=True)
    length: int = Column(Integer(), nullable=True)
    tracksort: int = Column(Integer(), nullable=True)
    genre: str = Column(String(), nullable=True)


class Album(Base):
    """A class representing an album in the music database."""
    __tablename__ = "albums"

    title: str = Column(Integer(), nullable=True)
    album_status: str = Column(String(), nullable=True)
    album_type: str = Column(String(), nullable=True)
    language: str = Column(String(), nullable=True)
    date_string: str = Column(String(), nullable=True)
    date_format: str = Column(String(), nullable=True)
    barcode: str = Column(String(), nullable=True)
    albumsort: int = Column(Integer(), nullable=True)


class Artist(Base):
    """A class representing an artist in the music database."""
    __tablename__ = "artists"

    name: str = Column(String(), nullable=True)
    country: str = Column(String(), nullable=True)
    general_genre: str = Column(String(), nullable=True)
    
    _formed_in_stamp: str = Column(String(), nullable=True)
    _formed_in_format: str = Column(String(), nullable=True)

    @property
    def formed_in(self) -> ID3Timestamp:
        return ID3Timestamp.strptime(self._formed_in_stamp, self._formed_in_format)
    
    @property.setter
    def formed_in(self, id3_timestamp: ID3Timestamp):
        self._formed_in_format = id3_timestamp.timeformat
        self._formed_in_stamp = id3_timestamp.timestamp

    _notes: str = Column(String(), nullable=True)
    @property
    def notes(self):
        return FormattedText(html=self._notes)
    
    @property.setter
    def notes(self, notes: FormattedText):
        self._notes = notes.html



class Label(Base):
    __tablename__ = "labels"

    name: str = Column(String(), nullable=True)


class Target(Base):
    """A class representing a target of a song in the music database."""
    __tablename__ = "targets"

    _file: str = Column(String())
    _path: str = Column(String())
    Song: Song = Column(ForeignKey("songs.id"))


class Lyrics(Base):
    """A class representing lyrics of a song in the music database."""
    __tablename__ = "lyrics"

    text: str = Column(Text())
    language: str = Column(String())
    Song: Song = Column(ForeignKey("songs.id"))


class Source(Base):
    """A class representing a source of a song in the music database."""
    __tablename__ = "sources"

    page_str: str = Column(String())
    url: str = Column(String())

    # polymorphic relation
    content_type: str = Column(String())
    content_id: int = Column(Integer())

    __mapper_args__ = {
        'polymorphic_on': content_type,
        'polymorphic_identity': 'source'
    }
"""
    content = relationship(
        "Base",
        primaryjoin=f"and_(Source.content_type=='{Song.__tablename__}', Base.id==Source.content_id)",
        uselist=False,
        viewonly=True,
        lazy="joined"
    )
"""


class SongArtist(Base):
    """A class representing the relationship between a song and an artist."""
    __tablename__ = "song_artists"

    song: Song = Column(ForeignKey("songs.id"))
    artist: Artist = Column(ForeignKey("artists.id"))
    is_feature: bool = Column(Boolean(), default=False)


class ArtistAlbum(Base):
    """A class representing the relationship between an album and an artist."""
    __tablename__ = "artist_albums"

    album: Album = Column(ForeignKey("albums.id"))
    artist: Artist = Column(ForeignKey("artists.id"))


class AlbumSong(Base):
    """A class representing the relationship between an album and an song."""
    __tablename__ = "album_songs"

    album: Album = Column(ForeignKey("albums.id"))
    song: Song = Column(ForeignKey("songs.id"))


class LabelAlbum(Base):
    __tablename__ = "label_albums"

    label: Label = Column(ForeignKey("labels.id"))
    album: Album = Column(ForeignKey("albums.id"))


class LabelArtist(Base):
    __tablename__ = "label_artists"

    label: Label = Column(ForeignKey("labels.id"))
    artist: Artist = Column(ForeignKey("artists.id"))


class ArtistSong(Base):
    __tablename__ = "artist_songs"

    artist: Artist = Column(ForeignKey("artists.id"))
    song: Song = Column(ForeignKey("songs.id"))
