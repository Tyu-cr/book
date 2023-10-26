from sqlalchemy import String, Column, Integer, DateTime

from .db_session import SqlAlchemyBase


class Books(SqlAlchemyBase):
    """
    Represent book in the database.
    """
    __tablename__: str = 'books'

    id: Column = Column(Integer, primary_key=True, autoincrement=True)
    # TODO: login = Column(String(50))
    user_id: Column = Column(Integer)
    title: Column = Column(String(255))
    authors: Column = Column(String(255))
    date: Column = Column(String(20))
    image: Column = Column(String(255))
    description: Column = Column(String(2000))
    language: Column = Column(String(20))
    count: Column = Column(String)
    href: Column = Column(String(255))
