import os

from celery import Celery

from app.services.prices import PricesService
from app.database import SessionLocal
from app.schemas import prices as prices_schemas

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get(
    "CELERY_RESULT_BACKEND", "redis://localhost:6379"
)


@celery.task(name="create_task")
def add_prices(prices_to_add: str):
    db = SessionLocal()

    price_schemas: prices_schemas.WritePrices = prices_schemas.WritePrices.parse_raw(
        prices_to_add
    )
    PricesService.add_prices(db, price_schemas.prices)

    def get_date(price):
        date_val = price.date
        date_val = date_val.replace(day=1)
        return date_val

    dates = set(map(get_date, price_schemas.prices))
    for date_to_update in dates:
        PricesService.update_season_coefficient(db, date_to_update)

    db.close()

    return True
