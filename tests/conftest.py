from collections.abc import Generator, Iterable
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from sqlalchemy_utils import create_database, database_exists

from src import models
from src.database import SessionLocal, engine
from src.main import app
from src.models import Base

from .factories import CurrencyFactory, ExchangeRateFactory


@pytest.fixture(scope="session")
def db() -> Session:
    # Factories commit on creation. Without expire_on_commit=False, reading a
    # fixture's attribute afterwards would open a new transaction (BEGIN
    # IMMEDIATE holds the write lock) and block the app's writes.
    db_session = SessionLocal(expire_on_commit=False)
    if not database_exists(engine.url):
        create_database(engine.url)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    # factory_boy types _meta as the base FactoryOptions
    CurrencyFactory._meta.sqlalchemy_session = db_session  # type: ignore[attr-defined]
    ExchangeRateFactory._meta.sqlalchemy_session = db_session  # type: ignore[attr-defined]
    return db_session


@pytest.fixture()
def cleanup_db(db: Session) -> None:
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())
    # Commit, or the open transaction keeps the write lock and blocks the app
    db.commit()


@pytest.fixture()
def app_client(cleanup_db: Any) -> Generator[TestClient]:
    yield TestClient(app)


@pytest.fixture()
def create_currency_eur() -> Generator[CurrencyFactory]:
    currency = CurrencyFactory()
    yield currency


@pytest.fixture()
def create_currency_usd() -> Generator[CurrencyFactory]:
    currency = CurrencyFactory(code="USD", name="US Dollar", sign="$")
    yield currency


@pytest.fixture()
def create_currency_gpb() -> Generator[CurrencyFactory]:
    currency = CurrencyFactory(code="GBP", name="Pound Sterling", sign="£")
    yield currency


@pytest.fixture()
def create_exc_rate_usd_eur(
    create_currency_usd: models.Currency, create_currency_eur: models.Currency
) -> Generator[ExchangeRateFactory]:
    exc_rate = ExchangeRateFactory(
        base_currency=create_currency_usd, target_currency=create_currency_eur, rate=1.1
    )
    yield exc_rate


@pytest.fixture()
def create_exc_rate_list(
    create_currency_usd: models.Currency,
    create_currency_eur: models.Currency,
    create_currency_gpb: models.Currency,
) -> Generator[Iterable[ExchangeRateFactory]]:
    usd_to_eur = ExchangeRateFactory(
        base_currency=create_currency_usd, target_currency=create_currency_eur, rate=1.1
    )
    usd_to_gbp = ExchangeRateFactory(
        base_currency=create_currency_usd,
        target_currency=create_currency_gpb,
        rate=1.52,
    )

    yield [usd_to_eur, usd_to_gbp]
