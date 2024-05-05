from typing import Any, Generator, Iterable
import pytest
from sqlalchemy_utils import create_database, database_exists
from src.models import Base
from src.database import create_session
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from src.main import app
from .factories import CurrencyFactory, ExchangeRateFactory


@pytest.fixture(scope="session")
def db():
    db_session = create_session()
    engine = db_session.bind
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    CurrencyFactory._meta.sqlalchemy_session = db_session
    ExchangeRateFactory._meta.sqlalchemy_session = db_session
    return db_session


@pytest.fixture()
def cleanup_db(db: Session) -> None:
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())


@pytest.fixture()
def app_client(cleanup_db: Any) -> Generator[TestClient, None, None]:
    yield TestClient(app)


@pytest.fixture()
def create_currency_eur() -> Generator[CurrencyFactory, None, None]:
    currency = CurrencyFactory()
    yield currency


@pytest.fixture()
def create_currency_usd() -> Generator[CurrencyFactory, None, None]:
    currency = CurrencyFactory(code="USD", name="US Dollar", sign="$")
    yield currency


@pytest.fixture()
def create_currency_gpb() -> Generator[CurrencyFactory, None, None]:
    currency = CurrencyFactory(code="GBP", name="Pound Sterling", sign="£")
    yield currency


@pytest.fixture()
def create_exc_rate_usd_eur(
    create_currency_usd, create_currency_eur
) -> Generator[ExchangeRateFactory, None, None]:
    exc_rate = ExchangeRateFactory(
        base_currency=create_currency_usd, target_currency=create_currency_eur, rate=1.1
    )
    yield exc_rate


@pytest.fixture()
def create_exc_rate_list(
    create_currency_usd, create_currency_eur, create_currency_gpb
) -> Generator[Iterable[ExchangeRateFactory], None, None]:
    usd_to_eur = ExchangeRateFactory(
        base_currency=create_currency_usd, target_currency=create_currency_eur, rate=1.1
    )
    usd_to_gbp = ExchangeRateFactory(
        base_currency=create_currency_usd,
        target_currency=create_currency_gpb,
        rate=1.52,
    )

    yield [usd_to_eur, usd_to_gbp]
