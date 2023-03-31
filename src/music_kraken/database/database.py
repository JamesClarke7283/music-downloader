
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pycountry
import sys
import os

# Add the parent directory of the src package to the Python module search path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

print(sys.path)
from music_kraken.database.data_models import Base
from music_kraken.objects.parents import MainObject
import music_kraken.objects as objects
import music_kraken.database.data_models as data_models


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
    def _set_matching_attributes(obj, db_obj):
        for attr in dir(obj):
            if not attr.startswith('__') and hasattr(db_obj, attr):
            try:
                setattr(db_obj, attr, getattr(obj, attr))
            except AttributeError as e:
                print("WARNING: An attribute error occurred", e)
        return db_obj

    @staticmethod
    def obj_to_database_obj(obj):
        """Converts a music_kraken object to a database object"""
        # Iterate through all classes in music_kraken.objects that inherit from MainObject
        for cls_name in dir(objects):
            cls = getattr(objects, cls_name)
            if isinstance(cls, type) and issubclass(cls, MainObject) and isinstance(obj, cls):
                # Find the corresponding database model class in music_kraken.database.data_models
                db_model_class_name = cls_name  # Assuming the class names are the same in both modules
                if hasattr(data_models, db_model_class_name):
                    db_model_class = getattr(data_models, db_model_class_name)
                    db_obj = db_model_class()
                    Database._set_matching_attributes(obj, db_obj)
                return db_obj

        # If no matching database model class is found, return None
        return None

    def session(self):
        """Returns a SQLalchemy session using the database's engine"""
        session = sessionmaker(bind=self.engine)
        return session

    def push(self, obj):
        """Adds a single object element to the database"""
        with self.session() as session:
            session.add(obj)
            session.commit()

    def pushMany(self, *objects):
        """Adds a arbitrary number of elements to the database"""
        with self.session() as session:
            for obj in objects:
                session.add(obj)
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
