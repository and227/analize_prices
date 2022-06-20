from datetime import date

from sqlalchemy.orm import Session
from sqlalchemy.sql import and_

from app.models import prices as prices_models
from app.schemas import prices as prices_schemas
from app.parser import calculate_update_season_coefficient


class PricesService:
    @staticmethod
    def get_prices(db: Session, offset: int, limit: int) -> list[prices_schemas.Price]:
        return db.query(prices_models.Price).offset(offset).limit(limit).all()

    @staticmethod
    def get_season_coefficients(
        db: Session, offset: int, limit: int
    ) -> list[prices_schemas.Coefficient]:
        return db.query(prices_models.Coefficient).offset(offset).limit(limit).all()

    @staticmethod
    def add_prices(db: Session, price_to_add: list[prices_schemas.Price]):
        for price in price_to_add:
            db_item = prices_models.Price(**price.dict())
            db.add(db_item)
        db.commit()

    @staticmethod
    def _get_prices_for_year_statement(db: Session, year: int):
        statement = (
            db.query(prices_models.Price)
            .filter(
                and_(
                    prices_models.Price.date >= f"{year}-01-01",
                    prices_models.Price.date < f"{year+1}-01-01",
                )
            )
            .statement
        )

        return statement

    @staticmethod
    def _update_season_coefficient(db: Session, new_value: float, update_month: str):
        db.query(prices_models.Coefficient).filter(
            prices_models.Coefficient.date == update_month
        ).update({"coefficient": new_value})
        db.commit()

    @classmethod
    def update_season_coefficient(cls, db: Session, date: date):
        statement = cls._get_prices_for_year_statement(db, date.year)
        update_month = date.strftime("%Y-%m-01")
        new_coefficient = calculate_update_season_coefficient(statement, update_month)
        cls._update_season_coefficient(db, new_coefficient, update_month)
