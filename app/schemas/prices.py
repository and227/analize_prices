from datetime import date

from pydantic import BaseModel


class Price(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float

    class Config:
        orm_mode = True


class WritePrices(BaseModel):
    prices: list[Price]


class Coefficient(BaseModel):
    date: date
    coefficient: float

    class Config:
        orm_mode = True
