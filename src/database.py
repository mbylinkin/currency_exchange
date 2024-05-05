from typing import Any, Generator, Iterable
from sqlalchemy import Insert, Select, Update, create_engine, exc

from sqlalchemy.orm import sessionmaker, Session

from src import settings
from src.exceptions import AlreadyExists

from sqlalchemy.pool import StaticPool

engine = create_engine(
    settings.app.database_url,
    echo=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def create_session() -> Session:
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    return Session()


def get_session() -> Generator[Session, None, None]:
    try:
        session = create_session()
        yield session
    finally:
        session.close()


def fetch_one(stmt: Select | Insert | Update) -> Iterable[Any] | None:
    with create_session() as session:
        item = session.scalars(stmt).first()
    return item


def fetch_all(stmt: Select | Insert | Update) -> Iterable[Any]:
    with create_session() as session:
        items = session.scalars(stmt).all()
    return items


def upd_one(item: Any) -> Any:
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
