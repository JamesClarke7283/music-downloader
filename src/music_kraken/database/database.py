# Standard library
from typing import Optional, Union, List
from enum import Enum
from playhouse.migrate import *

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy_utils import create_database, database_exists

# own modules
from . import (
    data_models,
    write
)
from .. import objects


class DatabaseType(Enum):
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"


Base = declarative_base()


class Album(Base):
    __tablename__ = 'album'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    artist_id = Column(Integer, ForeignKey('artist.id'))
    artist = relationship("Artist", back_populates="albums")
    songs = relationship("Song", back_populates="album")


class Artist(Base):
    __tablename__ = 'artist'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    albums = relationship("Album", back_populates="artist")
    songs = relationship("Song", back_populates="artist")


class Song(Base):
    __tablename__ = 'song'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    album_id = Column(Integer, ForeignKey('album.id'))
    album = relationship("Album", back_populates="songs")
    artist_id = Column(Integer, ForeignKey('artist.id'))
    artist = relationship("Artist", back_populates="songs")


class Database:
    def __init__(
            self,
            db_type: DatabaseType,
            db_name: str,
            db_user: Optional[str] = None,
            db_password: Optional[str] = None,
            db_host: Optional[str] = None,
            db_port: Optional[int] = None
    ):
        self.db_type = db_type
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port

        self.initialize_database()

    def create_engine(self) -> create_engine:
        """Create an engine instance based on the configured database type and parameters.

        Returns:
            The created engine instance, or None if an invalid database type was specified.
        """

        if self.db_type == DatabaseType.SQLITE:
            return create_engine(f'sqlite:///{self.db_name}')

        if self.db_type == DatabaseType.POSTGRESQL:
            connection_string = f'postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'
            return create_engine(connection_string)

        if self.db_type == DatabaseType.MYSQL:
            connection_string = f'mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}'
            return create_engine(connection_string)

        raise ValueError("Invalid database type specified.")

    def initialize_database(self):
        """
        Connect to the database,
        initialize the previously defined databases,
        create tables if they don't exist.
        """

        engine = self.create_engine()

        if not database_exists(engine.url):
            create_database(engine.url)

        Session = sessionmaker(bind=engine)
        session = Session()

        Base.metadata.create_all(engine)
