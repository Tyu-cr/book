from sqlalchemy import Column, Integer, String

from db_session import SqlAlchemyBase


class History(SqlAlchemyBase):
    __tablename__ = 'history'

    key = Column(Integer, primary_key=True, autoincrement=True)
    id = Column(String)
    title = Column(String)
    authors = Column(String)
    time = Column(String)
