import datetime

from sqlalchemy import Column, Integer, String, DateTime

from app.db.db_session import SqlAlchemyBase


class History(SqlAlchemyBase):
    """
    Represent history of search in the database.
    """
    __tablename__: str = 'history'

    key: Column = Column(Integer, primary_key=True, autoincrement=True)
    user_id: Column = Column(Integer)
    title: Column = Column(String)
    authors: Column = Column(String)
    time: Column = Column(DateTime, default=datetime.datetime.now)
