from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DataAccessLayer:
    def __init__(self, db: str):
        self.conn = f"sqlite:///{db}"
        self.engine = None

    def connect(self):
        self.engine = create_engine(self.conn)
        self.Session = sessionmaker(bind=self.engine)


@contextmanager
def session_scope(db: str):
    """
    Provides a transactional scope around series of operations.
    """
    dal = DataAccessLayer(db)
    dal.connect()
    session = dal.Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def insert_or_ignore(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).one_or_none()
    if not instance:
        instance = model(**kwargs)
        session.add(instance)
        session.flush()
        return instance
    else:
        return instance


def delete_instances(session, model, **kwargs) -> int:
    instances = session.query(model).filter_by(**kwargs).all()
    n = 0
    for i in instances:
        n += 1
        session.delete(i)
    return n
