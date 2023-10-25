import datetime

from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, DateTime
from werkzeug.security import generate_password_hash, check_password_hash

from db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    """
    Represents a user in the database.
    """

    def set_password(self, password: str) -> None:
        """
        Set the user's password.

        :param password: The new password.
        :type password: str
        """
        # TODO: expect Column?
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Check if the provided password matches the stored hashed password.

        :param password: The password to check.
        :type password: str
        :return: True if the passwords match, False otherwise.
        :rtype: bool
        """
        # TODO: except Column?
        return check_password_hash(self.hashed_password, password)

    __tablename__: str = 'users'

    id: Column = Column(Integer, primary_key=True, autoincrement=True)
    login: Column = Column(String(255))
    email: Column = Column(String(255), unique=True)
    hashed_password: Column = Column(String(255))
    modified_date: Column = Column(DateTime, default=datetime.datetime.utcnow)
