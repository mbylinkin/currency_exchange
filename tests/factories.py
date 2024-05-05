from src import models
import factory


class CurrencyFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Class for generating a fake currency element.
    """

    id = factory.Sequence(lambda n: n)
    code: str = "EUR"
    name: str = "Euro"
    sign: str = "€"

    class Meta:
        model = models.Currency
        sqlalchemy_session_persistence = "commit"


class ExchangeRateFactory(factory.alchemy.SQLAlchemyModelFactory):
    """
    Class for generating a fake exchange rate element.
    """

    id = factory.Sequence(lambda n: n)
    base_currency = factory.SubFactory(CurrencyFactory)
    target_currency = factory.SubFactory(CurrencyFactory)
    rate = 1.0

    class Meta:
        model = models.ExchangeRates
        sqlalchemy_session_persistence = "commit"
