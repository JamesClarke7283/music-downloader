from typing import List, Union, Type, Optional
from sqlalchemy import create_engine, Column, Integer, Boolean, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy_utils import create_database, database_exists

"""
**IMPORTANT**:

never delete, modify the datatype or add constrains to ANY existing collumns,
between the versions, that gets pushed out to the users.
Else my function can't update legacy databases, to new databases, 
while keeping the data of the old ones.

EVEN if that means to for example keep decimal values stored in strings.
(not in my codebase though.)
"""
Base = declarative_base()


class ObjectModel(Base):
    id: str = Column(String(), primary_key=True)


class MainModel(Base):
    additional_arguments: str = Column(String(), nullable=True)
    notes: str = Column(String(), nullable=True)


class Song(MainModel):
    """A class representing a song in the music database."""
    __tablename__ = "songs"
    id: int = Column(Integer(), primary_key=True)
    title: str = Column(String(), nullable=True)
    isrc: str = Column(String(), nullable=True)
    length: int = Column(Integer(), nullable=True)
    tracksort: int = Column(Integer(), nullable=True)
    genre: str = Column(String(), nullable=True)
    

class Album(MainModel):
    """A class representing an album in the music database."""
    __tablename__ = "albums"
    id: int = Column(Integer(), primary_key=True)
    title: str = Column(Integer(), nullable=True)
    album_status: str = Column(String(), nullable=True)
    album_type: str = Column(String(), nullable=True)
    language: str = Column(String(), nullable=True)
    date_string: str = Column(String(), nullable=True)
    date_format: str = Column(String(), nullable=True)
    barcode: str = Column(String(), nullable=True)
    albumsort: int = Column(Integer(), nullable=True)


class Artist(MainModel):
    """A class representing an artist in the music database."""
    id: int = Column(Integer(), primary_key=True)
    name: str = Column(String(), nullable=True)
    country: str = Column(String(), nullable=True)
    formed_in_date: str = Column(String(), nullable=True)
    formed_in_format: str = Column(String(), nullable=True)
    general_genre: str = Column(String(), nullable=True)


class Label(MainModel):
    id: int = Column(Integer(), primary_key=True) 
    name: str = Column(String(), nullable=True)


class Target(ObjectModel):
    """A class representing a target of a song in the music database."""
    __tablename__ = "targets"
    file: str = Column(String())
    path: str = Column(String())
    song: Song = Column(ForeignKey("songs.id"))


class Lyrics(ObjectModel):
    """A class representing lyrics of a song in the music database."""
    __tablename__ = "lyrics"
    text: str = Column(Text())
    language: str = Column(String())
    song: Song = Column(ForeignKey("songs.id"))


class Source(Base):
    """A class representing a source of a song in the music database."""
    __tablename__ = "sources"

    id: int = Column(Integer(), primary_key=True)
    page: str = Column(String())
    url: str = Column(String())
    content_type: str = Column(String())
    content_id: int = Column(Integer())

    __mapper_args__ = {
        'polymorphic_on': content_type,
        'polymorphic_identity': 'source'
    }

    content: Union[Song, Album, Artist, Lyrics, Label] = relationship(
        "ObjectModel",
        primaryjoin=f"and_(Source.content_type=='{Song.__tablename__}', ObjectModel.id==Source.content_id)",
        uselist=False,
        viewonly=True,
        lazy="joined"
    )




class SongArtist(Base):
    """A class representing the relationship between a song and an artist."""
    __tablename__ = "song_artists"
    id: int = Column(Integer(), primary_key=True)
    song: Song = Column(ForeignKey("songs.id"))
    artist: Artist = Column(ForeignKey("artists.id"))
    is_feature: bool = Column(Boolean(), default=False)


class ArtistAlbum(Base):
    """A class representing the relationship between an album and an artist."""
    id: int = Column(Integer(), primary_key=True)
    album: Album = Column(ForeignKey("albums.id"))
    artist: Artist = Column(ForeignKey("artists.id"))


class AlbumSong(Base):
    """A class representing the relationship between an album and an song."""
    album: Album = Column(ForeignKey("albums.id"))
    song: Song = Column(ForeignKey("songs.id"))


class LabelAlbum(Base):
    label: Label = Column(ForeignKey("labels.id"))
    album: Album = Column(ForeignKey("albums.id"))


class LabelArtist(Base):
    label: Label = Column(ForeignKey("labels.id"))
    artist: Artist = Column(ForeignKey("artists.id"))


ALL_MODELS = [
    Song,
    Album,
    Artist,
    Source,
    Lyrics,
    ArtistAlbum,
    Target,
    SongArtist
]
