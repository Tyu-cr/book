from sqlalchemy import String, Column, Integer

from db_session import SqlAlchemyBase


class Books(SqlAlchemyBase):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(50))
    title = Column(String(255))
    authors = Column(String(255))
    date = Column(String(255))
    image = Column(String(255))
    description = Column(String(255))
    language = Column(String(255))
    # TODO: count = Column(String) ???
    count = Column(Integer)
    href = Column(String(255))
