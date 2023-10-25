import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

SqlAlchemyBase = declarative_base()

__factory = None


def global_init(db_file):
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise Exception('Database file must be specified.')

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f'Connecting to database: {conn_str}')

    engine = sa.create_engine(conn_str, echo=False)
    __factory = sessionmaker(bind=engine)

    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    global __factory
    return __factory()
