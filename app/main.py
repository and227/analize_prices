import asyncio

from fastapi import FastAPI, Depends, status
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.parser import parse_prices
from app.models import prices as prices_models
from app.schemas import prices as prices_schemas
from app.services.prices import PricesService
from app.database import SessionLocal, engine
from app.worker import add_prices


prices_models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, parse_prices)


@app.get("/prices", response_model=list[prices_schemas.Price])
def get_prices(db: Session = Depends(get_db), offset: int = 0, limit: int = 100):
    return PricesService.get_prices(db, offset, limit)


@app.get("/season_coefficients", response_model=list[prices_schemas.Coefficient])
def get_season_coefficients(
    db: Session = Depends(get_db), offset: int = 0, limit: int = 100
):
    return PricesService.get_season_coefficients(db, offset, limit)


@app.post("/prices", status_code=status.HTTP_201_CREATED)
def add_price(prices_to_add: prices_schemas.WritePrices):
    add_prices.apply_async(args=(prices_to_add.json(),))
    return "New price added"
