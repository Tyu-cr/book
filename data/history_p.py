import sqlalchemy
from .db_session import SqlAlchemyBase


class History(SqlAlchemyBase):
    __tablename__ = "history"

    key = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    id = sqlalchemy.Column(sqlalchemy.String)
    title = sqlalchemy.Column(sqlalchemy.String)
    authors = sqlalchemy.Column(sqlalchemy.String)
    time = sqlalchemy.Column(sqlalchemy.String)
