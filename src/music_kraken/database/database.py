from typing import Dict, Optional, Set, Type, Iterable
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ..utils.shared import DATABASE_LOGGER as LOGGER
from . import data_models
from .data_models import Base
from .. import objects
from ..objects import DatabaseObject


ALL_DATA_OBJECTS: Dict[Type[DatabaseObject], Type[Base]] = {
    objects.Song: data_models.Song,
    objects.Album: data_models.Album,
    objects.Artist: data_models. Artist,
    objects.Label: data_models.Label,
    objects.Target: data_models.Target,
    objects.Lyrics: data_models.Lyrics,
    objects.Source: data_models.Source
}


class Database:
    """A class representing a database.
    It returns an engine, which can be used to create a session.

    Examples:
        db = Database("sqlite:///music_kraken.db")
        db_memory = Database("sqlite:///:memory:") 
    """
    def __init__(self, db_string: str):
        self.engine = create_engine(db_string)
        Base.metadata.create_all(self.engine)

    @staticmethod
    def _set_matching_attributes(data_object: DatabaseObject, data_model: Base) -> Base:
        model_attributes: Set[str] = set(attr for attr in dir(data_model))

        data_model.id = data_object.id

        attribute: str
        for attribute in data_object.SIMPLE_ATTRIBUTES.keys():
            if attribute not in model_attributes:
                raise AttributeError(f"the attributes ({attribute}) of {type(DatabaseObject)} are not synced up with those of {type(data_model)}")
            
            setattr(data_model, attribute, getattr(data_object, attribute))

        return data_model

    @classmethod
    def _obj_to_database_obj(cls, data_object: DatabaseObject) -> Base:
        """Converts a music_kraken object to a database object"""
        # Iterate through all classes in music_kraken.objects that inherit from MainObject

        model_type: Optional[Type[Base]] = ALL_DATA_OBJECTS.get(type(data_object))
        if model_type is None:
            return None

        return cls._set_matching_attributes(data_object, model_type())

    def session(self):
        """Returns a SQLalchemy session using the database's engine"""
        session = sessionmaker(bind=self.engine)
        return session

    def push(self, data_object: DatabaseObject):
        """
        Adds a single object element to the database
        """
        model = self.__class__._obj_to_database_obj(data_object)
        if model is None:
            return

        with self.session() as session:
            session.add(model)
            session.commit()

    def pushMany(self, *data_objects: Iterable[DatabaseObject]):
        """
        Adds a arbitrary number of elements to the database
        """
        
        with self.session() as session:
            for data_object in data_objects:
                model = self.__class__._obj_to_database_obj(data_object)
                if model is None:
                    continue

                session.add(model)
            session.commit()

    def pull(self, obj, **filter_by):
        """Gets a singular object from the database by its type of obj, and using the filter_by"""
        with self.session() as session:
            returned_obj = session.query(obj).filter_by(**filter_by).first()
            return returned_obj

    def pullMany(self, obj, **filter_by):
        """Gets all the elements found by the filter_by, from the database, of the type obj"""
        with self.session() as session:
            returned_obj = session.query(obj).filter_by(**filter_by).all()
            return returned_obj

    def commit(self):
        """Commits changes made to pulled objects, to the database"""
        with self.session() as session:
            session.commit()

    def delete(self, obj):
        """Deletes an object from the database"""
        with self.session() as session:
            session.delete(obj)
            session.commit()

    def deleteMany(self, *objects):
        """Deletes an arbitrary number of objects from the database"""
        with self.session() as session:
            for obj in objects:
                session.delete(obj)
            session.commit()
