from typing import Optional, Union
from sqlalchemy import Column, Integer, Boolean, String, Text, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

from ..objects import FormattedText, ID3Timestamp, AlbumStatus, AlbumType
import pycountry

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
    unified_title: str = Column(String(), nullable=True)
    isrc: str = Column(String(), nullable=True)
    length: int = Column(Integer(), nullable=True)
    tracksort: int = Column(Integer(), nullable=True)
    genre: str = Column(String(), nullable=True)

    Artist = relationship("Artist", secondary="song_artists")
    _notes: str = Column(String(), nullable=True)

    @property
    def notes(self):
        return FormattedText(html=self._notes)

    @notes.setter
    def notes(self, notes: FormattedText):
        self._notes = notes.html


class Artwork(Base):
    __tablename__ = "artworks"

    album_id: int = Column(Integer(), ForeignKey("albums.id"), nullable=True)
    artist_id: int = Column(Integer(), ForeignKey("artists.id"), nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(
            [album_id, artist_id],
            ["albums.id", "artists.id"],
            use_alter=True,
            name="artwork_album_artist_fk"
        ),
    )

    content_type: str = Column(String())
    content_id: int = Column(Integer())

    __mapper_args__ = {
        'polymorphic_on': content_type,
        'polymorphic_identity': 'artwork'
    }

    Album = relationship("Album", back_populates="artworks", foreign_keys=[album_id])
    Artist = relationship("Artist", back_populates="artworks", foreign_keys=[artist_id])


class Album(Base):
    """A class representing an album in the music database."""
    __tablename__ = "albums"

    title: str = Column(String(), nullable=True)
    unified_title: str = Column(String(), nullable=True)
    _album_status: str = Column(String(), nullable=True)
    _album_type: str = Column(String(), nullable=True)
    _language: str = Column(String(), nullable=True)
    _date_string: str = Column(String(), nullable=True)
    _date_format: str = Column(String(), nullable=True)
    barcode: str = Column(String(), nullable=True)
    albumsort: int = Column(Integer(), nullable=True)
    # Is actually a list of artworks
    Artwork = relationship("Artwork", back_populates="album", foreign_keys="Artwork.album_id")

    Label = relationship("Label", back_populates="album", foreign_keys="LabelAlbum.label_id")
    Artist = relationship("Artist", back_populates="album", foreign_keys="ArtistAlbum.artist_id")

    _notes: str = Column(String(), nullable=True)

    @property
    def notes(self):
        return FormattedText(html=self._notes)

    @notes.setter
    def notes(self, notes: FormattedText):
        self._notes = notes.html

    @property
    def album_status(self):
        return AlbumStatus(self._album_status)

    @album_status.setter
    def album_status(self, status: AlbumStatus):
        self._album_status = status.value

    @property
    def album_type(self):
        return AlbumType(self._album_type)

    @album_type.setter
    def album_type(self, album_type: AlbumType):
        self._album_type = album_type.value

    @property
    def language(self):
        return pycountry.languages.get(alpha_3=self._language)

    @language.setter
    def language(self, language: Optional[pycountry.languages]):
        if language is None:
            self._language = None
        else:
            self._language = language.alpha_3
    
    @property
    def date(self) -> ID3Timestamp:
        return ID3Timestamp.strptime(self._date_string, self._date_format)

    @date.setter
    def date(self, id3_timestamp: ID3Timestamp):
        self._date_format = id3_timestamp.timeformat
        self._date_string = id3_timestamp.timestamp


class Artist(Base):
    """A class representing an artist in the music database."""
    __tablename__ = "artists"

    name: str = Column(String(), nullable=True)
    country: str = Column(String(), nullable=True)
    general_genre: str = Column(String(), nullable=True)
    # Is actually a list of artworks
    Artwork = relationship("Artwork", back_populates="artist", foreign_keys="Artwork.artist_id")

    _formed_in_stamp: str = Column(String(), nullable=True)
    _formed_in_format: str = Column(String(), nullable=True)

    @property
    def formed_in(self) -> ID3Timestamp:
        return ID3Timestamp.strptime(self._formed_in_stamp, self._formed_in_format)

    @formed_in.setter
    def formed_in(self, id3_timestamp: ID3Timestamp):
        self._formed_in_format = id3_timestamp.timeformat
        self._formed_in_stamp = id3_timestamp.timestamp

    _notes: str = Column(String(), nullable=True)
    @property
    def notes(self):
        return FormattedText(html=self._notes)

    @notes.setter
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
