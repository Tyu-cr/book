from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from db_session import SqlAlchemyBase


class History(SqlAlchemyBase):
    """
    Represent history of search in the database.
    """
    __tablename__: str = 'history'

    key: Column = Column(Integer, primary_key=True, autoincrement=True)
    # TODO: id: Column = Column(String) ???
    user_id: Column = Column(Integer)
    title: Column = Column(String)
    authors: Column = Column(String)
    # TODO: time: Column = Column(String) ???
    time: Column = Column(DateTime, default=datetime.now)
