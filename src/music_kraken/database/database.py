# Standard library
from typing import Optional, Union, List
from enum import Enum

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from data_models import Base


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
