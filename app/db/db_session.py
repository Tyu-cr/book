import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

SqlAlchemyBase = declarative_base()

__factory = None


def global_init(db_file: str) -> None:
    """
    Initialize the database connection.

    :param db_file: Path to the database file.
    :type db_file: str
    :raises Exception: No database name or error initializing database.
    """
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception('Database file must be specified.')

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'

    print(f'Connecting to database: {conn_str}')

    try:
        engine = sa.create_engine(conn_str, echo=False)
        __factory = sessionmaker(bind=engine)

        SqlAlchemyBase.metadata.create_all(engine)
    except Exception as e:
        raise Exception(f'Error initializing database: {e}')


def create_session() -> Session:
    """
    Create a new session.

    :return: A new SQLAlchemy session.
    :rtype: Session
    """
    global __factory
    return __factory()
