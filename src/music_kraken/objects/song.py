import os
from typing import List, Optional, Type, Dict
import pycountry

from .metadata import (
    Mapping as id3Mapping,
    ID3Timestamp,
    MetadataAttribute
)
from ..utils.shared import (
    MUSIC_DIR,
    DATABASE_LOGGER as LOGGER
)
from .parents import (
    DatabaseObject,
    MainObject
)
from .source import (
    Source,
    SourceTypes,
    SourcePages,
    SourceAttribute
)
from .formatted_text import FormattedText
from .collection import Collection
from .album import AlbumType, AlbumStatus
from .lyrics import Lyrics
from .target import Target

"""
All Objects dependent 
"""

CountryTyping = type(list(pycountry.countries)[0])


class Song(MainObject, SourceAttribute, MetadataAttribute):
    """
    Class representing a song object, with attributes id, mb_id, title, album_name, isrc, length,
    tracksort, genre, source_list, target, lyrics_list, album, main_artist_list, and feature_artist_list.

    Inherits from DatabaseObject, SourceAttribute, and MetadataAttribute classes.
    """

    def __init__(
            self,
            _id: str = None,
            dynamic: bool = False,
            title: str = None,
            isrc: str = None,
            length: int = None,
            tracksort: int = None,
            genre: str = None,
            source_list: List[Source] = None,
            target_list: List[Target] = None,
            lyrics_list: List[Lyrics] = None,
            album_list: Type['Album'] = None,
            main_artist_list: List[Type['Artist']] = None,
            feature_artist_list: List[Type['Artist']] = None,
            **kwargs
    ) -> None:
        """
        Initializes the Song object with the following attributes:
        """
        MainObject.__init__(self, _id=_id, dynamic=dynamic, **kwargs)
        # attributes
        self.title: str = title
        self.isrc: str = isrc
        self.length: int = length
        self.tracksort: int = tracksort or 0
        self.genre: str = genre

        self.source_list = source_list or []

        self.target_list = target_list or []

        self.lyrics_collection: Collection = Collection(
            data=lyrics_list or [],
            map_attributes=[],
            element_type=Lyrics
        )

        self.album_collection: Collection = Collection(
            data=album_list or [],
            map_attributes=["title"],
            element_type=Album
        )

        self.main_artist_collection = Collection(
            data=main_artist_list or [],
            map_attributes=["title"],
            element_type=Artist
        )
        self.feature_artist_collection = Collection(
            data=feature_artist_list or [],
            map_attributes=["title"],
            element_type=Artist
        )

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self.id == other.id

    def get_artist_credits(self) -> str:
        main_artists = ", ".join([artist.name for artist in self.main_artist_collection])
        feature_artists = ", ".join([artist.name for artist in self.feature_artist_collection])

        if len(feature_artists) == 0:
            return main_artists
        return f"{main_artists} feat. {feature_artists}"

    def __str__(self) -> str:
        artist_credit_str = ""
        artist_credits = self.get_artist_credits()
        if artist_credits != "":
            artist_credit_str = f" by {artist_credits}"

        return f"\"{self.title}\"{artist_credit_str}"

    def __repr__(self) -> str:
        return f"Song(\"{self.title}\")"

    def get_tracksort_str(self):
        """
        if the album tracklist is empty, it sets it length to 1, this song has to be in the Album
        :returns id3_tracksort: {song_position}/{album.length_of_tracklist} 
        """
        return f"{self.tracksort}/{len(self.album.tracklist) or 1}"

    def get_metadata(self) -> MetadataAttribute.Metadata:
        metadata = MetadataAttribute.Metadata({
            id3Mapping.TITLE: [self.title],
            id3Mapping.ISRC: [self.isrc],
            id3Mapping.LENGTH: [self.length],
            id3Mapping.GENRE: [self.genre],
            id3Mapping.TRACKNUMBER: [self.tracksort_str]
        })

        metadata.merge_many([s.get_song_metadata() for s in self.source_list])
        metadata.merge_many([a.metadata for a in self.album_collection])
        metadata.merge_many([a.metadata for a in self.main_artist_collection])
        metadata.merge_many([a.metadata for a in self.feature_artist_collection])
        metadata.merge_many([lyrics.metadata for lyrics in self.lyrics_collection])

        return metadata

    def get_options(self) -> list:
        """
        Return a list of related objects including the song object, album object, main artist objects, and feature artist objects.

        :return: a list of objects that are related to the Song object
        """
        options = self.main_artist_list.copy()
        options.extend(self.feature_artist_collection)
        options.extend(self.album_collection)
        options.append(self)
        return options

    def get_option_string(self) -> str:
        return f"Song({self.title}) of Album({self.album.title}) from Artists({self.get_artist_credits()})"

    tracksort_str: List[Type['Album']] = property(fget=get_tracksort_str)
    main_artist_list: List[Type['Artist']] = property(fget=lambda self: self.main_artist_collection.copy())
    feature_artist_list: List[Type['Artist']] = property(fget=lambda self: self.feature_artist_collection.copy())

    album_list: List[Type['Album']] = property(fget=lambda self: self.album_collection.copy())
    lyrics_list: List[Type[Lyrics]] = property(fget=lambda self: self.lyrics_collection.copy())


"""
All objects dependent on Album
"""


class Album(MainObject, SourceAttribute, MetadataAttribute):
    def __init__(
            self,
            _id: str = None,
            title: str = None,
            language: pycountry.Languages = None,
            date: ID3Timestamp = None,
            barcode: str = None,
            is_split: bool = False,
            albumsort: int = None,
            dynamic: bool = False,
            source_list: List[Source] = None,
            artist_list: list = None,
            song_list: List[Song] = None,
            album_status: AlbumStatus = None,
            album_type: AlbumType = None,
            label_list: List[Type['Label']] = None,
            **kwargs
    ) -> None:
        MainObject.__init__(self, _id=_id, dynamic=dynamic, **kwargs)

        self.title: str = title
        self.album_status: AlbumStatus = album_status
        self.album_type: AlbumType = album_type
        self.language: pycountry.Languages = language
        self.date: ID3Timestamp = date or ID3Timestamp()

        """
        TODO
        find out the id3 tag for barcode and implement it
        maybe look at how mutagen does it with easy_id3
        """
        self.barcode: str = barcode
        """
        TODO
        implement a function in the Artist class,
        to set albumsort with help of the release year
        """
        self.albumsort: Optional[int] = albumsort

        self.song_collection: Collection = Collection(
            data=song_list or [],
            map_attributes=["title"],
            element_type=Song
        )

        self.artist_collection: Collection = Collection(
            data=artist_list or [],
            map_attributes=["name"],
            element_type=Artist
        )

        self.label_collection: Collection = Collection(
            data=label_list,
            map_attributes=["name"],
            element_type=Label
        )

        self.source_list = source_list or []

    def __repr__(self):
        return f"Album(\"{self.title}\")"

    def update_tracksort(self):
        """
        This updates the tracksort attributes, of the songs in
        `self.song_collection`, and sorts the songs, if possible.

        It is advised to only call this function, once all the tracks are
        added to the songs.

        :return:
        """

        tracksort_map: Dict[int, Song] = {song.tracksort: song for song in self.song_collection if
                                          song.tracksort is not None}

        # place the songs, with set tracksort attribute according to it
        for tracksort, song in tracksort_map.items():
            index = tracksort - 1

            """
            I ONLY modify the `Collection._data` attribute directly, 
            to bypass the mapping of the attributes, because I will add the item in the next step
            """
            self.song_collection._data.remove(song)
            self.song_collection._data.insert(index, song)

        # fill in the empty tracksort attributes
        for i, song in enumerate(self.song_collection):
            if song.tracksort is not None:
                continue
            song.tracksort = i + 1

    def get_metadata(self) -> MetadataAttribute.Metadata:
        return MetadataAttribute.Metadata({
            id3Mapping.ALBUM: [self.title],
            id3Mapping.COPYRIGHT: [self.copyright],
            id3Mapping.LANGUAGE: [self.iso_639_2_language],
            id3Mapping.ALBUM_ARTIST: [a.name for a in self.artist_collection],
            id3Mapping.DATE: [self.date.timestamp]
        })

    def get_copyright(self) -> str:
        if self.date is None:
            return ""
        if self.date.has_year or len(self.label_collection) == 0:
            return ""

        return f"{self.date.year} {self.label_collection[0].name}"

    @property
    def iso_639_2_lang(self) -> Optional[str]:
        if self.language is None:
            return None

        return self.language.alpha_3

    @property
    def is_split(self) -> bool:
        """
        A split Album is an Album from more than one Artists
        usually half the songs are made by one Artist, the other half by the other one.
        In this case split means either that or one artist featured by all songs.
        :return:
        """
        return len(self.artist_collection) > 1

    def get_options(self) -> list:
        options = self.artist_collection.copy()
        options.append(self)
        options.extend(self.song_collection)

        return options

    def get_option_string(self) -> str:
        return f"Album: {self.title}; Artists {', '.join([i.name for i in self.artist_collection])}"

    label_list: List[Type['Label']] = property(fget=lambda self: self.label_collection.copy())
    artist_list: List[Type['Artist']] = property(fget=lambda self: self.artist_collection.copy())
    song_list: List[Song] = property(fget=lambda self: self.song_collection.copy())
    tracklist: List[Song] = property(fget=lambda self: self.song_collection.copy())

    copyright = property(fget=get_copyright)

"""
All objects dependent on Artist
"""


class Artist(MainObject, SourceAttribute, MetadataAttribute):
    def __init__(
            self,
            _id: str = None,
            dynamic: bool = False,
            name: str = None,
            source_list: List[Source] = None,
            feature_song_list: List[Song] = None,
            main_album_list: List[Album] = None,
            notes: FormattedText = None,
            lyrical_themes: List[str] = None,
            general_genre: str = "",
            country: CountryTyping = None,
            formed_in: ID3Timestamp = None,
            label_list: List[Type['Label']] = None,
            **kwargs
    ):
        MainObject.__init__(self, _id=_id, dynamic=dynamic, **kwargs)

        self.name: str = name

        """
        TODO implement album type and notes
        """
        self.country: CountryTyping = country
        self.formed_in: ID3Timestamp = formed_in
        """
        notes, generall genre, lyrics themes are attributes
        which are meant to only use in outputs to describe the object
        i mean do as you want but there aint no strict rule about em so good luck
        """
        self.notes: FormattedText = notes or FormattedText()
        """
        TODO
        implement in db
        """
        self.lyrical_themes: List[str] = lyrical_themes or []
        self.general_genre = general_genre

        self.feature_song_collection: Collection = Collection(
            data=feature_song_list,
            map_attributes=["title"],
            element_type=Song
        )

        self.main_album_collection: Collection = Collection(
            data=main_album_list,
            map_attributes=["title"],
            element_type=Album
        )

        self.label_collection: Collection = Collection(
            data=label_list,
            map_attributes=["name"],
            element_type=Label
        )

        self.source_list = source_list or []

    def __str__(self):
        string = self.name or ""
        plaintext_notes = self.notes.get_plaintext()
        if plaintext_notes is not None:
            string += "\n" + plaintext_notes
        return string

    def __repr__(self):
        return f"Artist(\"{self.name}\")"

    @property
    def country_string(self):
        return self.country.alpha_3

    def update_albumsort(self):
        """
        This updates the albumsort attributes, of the albums in
        `self.main_album_collection`, and sorts the albums, if possible.

        It is advised to only call this function, once all the albums are
        added to the artist.

        :return:
        """
        self.main_album_collection.sort(key=lambda _album: _album.date)

        for i, album in enumerate(self.main_album_collection):
            if album.albumsort is None:
                continue
            album.albumsort = i + 1

    def get_features(self) -> Album:
        feature_release = Album(
            title="features",
            album_status=AlbumStatus.UNRELEASED,
            album_type=AlbumType.COMPILATION_ALBUM,
            is_split=True,
            albumsort=666,
            dynamic=True,
            song_list=self.feature_song_collection.copy()
        )

        return feature_release

    def get_metadata(self) -> MetadataAttribute.Metadata:
        metadata = MetadataAttribute.Metadata({
            id3Mapping.ARTIST: [self.name]
        })
        metadata.merge_many([s.get_artist_metadata() for s in self.source_list])

        return metadata

    def get_options(self) -> list:
        options = [self]
        options.extend(self.main_album_collection)
        options.extend(self.feature_song_collection)
        return options

    def get_option_string(self) -> str:
        return f"Artist: {self.name}"

    def get_all_songs(self) -> List[Song]:
        """
        returns a list of all Songs.
        probably not that useful, because it is unsorted
        """
        collection = self.feature_song_collection.copy()
        for album in self.discography:
            collection.extend(album.song_collection)

        return collection

    def get_discography(self) -> List[Album]:
        flat_copy_discography = self.main_album_collection.copy()
        flat_copy_discography.append(self.get_features())

        return flat_copy_discography

    album_list: List[Album] = property(fget=lambda self: self.album_collection.copy())

    complete_album_list: List[Album] = property(fget=get_discography)
    discography: List[Album] = property(fget=get_discography)

    feature_album: Album = property(fget=get_features)
    song_list: List[Song] = property(fget=get_all_songs)
    label_list: List[Type['Label']] = property(fget=lambda self: self.label_collection.copy())


"""
Label
"""


class Label(MainObject, SourceAttribute, MetadataAttribute):
    def __init__(
            self,
            _id: str = None,
            dynamic: bool = False,
            name: str = None,
            album_list: List[Album] = None,
            current_artist_list: List[Artist] = None,
            source_list: List[Source] = None,
            **kwargs
    ):
        MainObject.__init__(self, _id=_id, dynamic=dynamic, **kwargs)

        self.name: str = name

        self.album_collection: Collection = Collection(
            data=album_list,
            map_attributes=["title"],
            element_type=Album
        )

        self.current_artist_collection: Collection = Collection(
            data=current_artist_list,
            map_attributes=["name"],
            element_type=Artist
        )

        self.source_list = source_list or []

    @property
    def album_list(self) -> List[Album]:
        return self.album_collection.copy()

    @property
    def current_artist_list(self) -> List[Artist]:
        self.current_artist_collection.copy()
