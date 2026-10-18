from collections.abc import Sequence

from sqlalchemy import Select, create_engine, exc
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src import settings
from src.exceptions import AlreadyExists

engine = create_engine(
    settings.app.database_url,
    echo=settings.app.debug,  # log SQL only in debug
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def create_session() -> Session:
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return Session()


def fetch_one[T](stmt: Select[T]) -> T | None:
    with create_session() as session:
        item = session.scalars(stmt).first()
    return item


def fetch_all[T](stmt: Select[T]) -> Sequence[T]:
    with create_session() as session:
        items = session.scalars(stmt).all()
    return items


def upd_one[T](item: T) -> T:
    with create_session() as session:
        try:
            session.add(item)
            session.commit()
            session.refresh(item)
        except exc.IntegrityError:
            session.rollback()
            raise AlreadyExists
        # except exc.SQLAlchemyError:
        #     raise DatabaseError

    return item
