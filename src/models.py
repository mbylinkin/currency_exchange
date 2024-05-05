import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column

from src import constants


class Base(DeclarativeBase):
    metadata = sa.MetaData(naming_convention=constants.DB_NAMING_CONVENTION)

    repr_cols_num = 3
    repr_cols = tuple()

    def __repr__(self) -> str:
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"


class Currency(Base):
    __tablename__ = "currency"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    code: Mapped[str] = mapped_column(sa.String(3))
    name: Mapped[str]
    sign: Mapped[str] = mapped_column(sa.String(1))

    __table_args__ = (sa.UniqueConstraint("code", name="currency_code_idx"),)


class ExchangeRates(Base):
    __tablename__ = "exchange_rates"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    base_currency_id = sa.Column(sa.Integer, sa.ForeignKey("currency.id"))
    target_currency_id = sa.Column(sa.Integer, sa.ForeignKey("currency.id"))
    rate = sa.Column(sa.DECIMAL(10, 6))

    base_currency: Mapped["Currency"] = relationship(
        foreign_keys=[base_currency_id], lazy="joined", innerjoin=True
    )
    target_currency: Mapped["Currency"] = relationship(
        foreign_keys=[target_currency_id], lazy="joined", innerjoin=True
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "base_currency_id", "target_currency_id", name="base_target_currency_idx"
        ),
    )
