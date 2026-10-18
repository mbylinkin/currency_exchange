import pytest
from sqlalchemy import exc
from sqlalchemy.orm import Session

from src import models


@pytest.mark.parametrize("column", ["base_currency_id", "target_currency_id", "rate"])
def test_exchange_rate_columns_are_not_nullable(
    db: Session,
    cleanup_db: None,
    create_currency_usd: models.Currency,
    create_currency_eur: models.Currency,
    column: str,
) -> None:
    values = {
        "base_currency_id": create_currency_usd.id,
        "target_currency_id": create_currency_eur.id,
        "rate": 1,
        column: None,
    }
    db.add(models.ExchangeRates(**values))

    with pytest.raises(exc.IntegrityError, match="NOT NULL"):
        db.commit()
    db.rollback()
