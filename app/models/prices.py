from sqlalchemy import Column, Date, Float

__all__ = ["Price", "Coefficient"]

from app.database import Base
from app.constants import PRICES_TABLE_NAME, COEFFICIENTS_TABLE_NAME


class Price(Base):
    __tablename__ = PRICES_TABLE_NAME

    date = Column(Date, primary_key=True, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)


class Coefficient(Base):
    __tablename__ = COEFFICIENTS_TABLE_NAME

    date = Column(Date, primary_key=True, index=True)
    coefficient = Column(Float)
