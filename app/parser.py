from pandas import read_csv, DataFrame, read_sql, Grouper, to_datetime

from app.settings import settings
from app.constants import PRICES_TABLE_NAME, COEFFICIENTS_TABLE_NAME
from app.database import engine


def prepare_data_frame() -> DataFrame:
    column_names = ["quote_name", "date", "open", "high", "low", "close"]
    data: DataFrame = read_csv(settings.INPUT_FILE_NAME, sep=",", names=column_names)

    def reformat_date(date):
        date_parts = date.split("/")
        changed_date = "-".join([date_parts[2], date_parts[0], date_parts[1]])
        return changed_date

    data["date"] = data["date"].apply(reformat_date)
    data["date"] = to_datetime(data["date"])
    data.set_index("date", inplace=True)

    return data


def calculate_season_coefficients(data: DataFrame) -> DataFrame:
    data["avg_price"] = data[["open", "high", "low", "close"]].mean(axis=1)
    data["month_price"] = data.groupby(Grouper(freq="M"))["avg_price"].transform("mean")
    data["year_price"] = data.groupby(Grouper(freq="Y"))["avg_price"].transform("mean")
    data["coefficient"] = data["month_price"] / data["year_price"]
    grouped_data = data.groupby(Grouper(freq="M")).mean()
    grouped_data = grouped_data.reset_index()
    grouped_data["date"] = grouped_data["date"].apply(lambda x: x.strftime("%Y-%m-01"))
    grouped_data.set_index("date", inplace=True)

    return grouped_data


def is_data_in_db(table_name):
    existing_data = read_sql(table_name, con=engine)
    return len(existing_data) > 0


def write_prices_to_db(data: DataFrame):
    data.drop("quote_name", axis=1, inplace=True)
    data.to_sql(PRICES_TABLE_NAME, con=engine, if_exists="append")


def write_coefficients_to_db(data: DataFrame):
    data.drop(
        [
            "avg_price",
            "month_price",
            "year_price",
            "open",
            "high",
            "low",
            "close",
        ],
        axis=1,
        inplace=True,
    )
    data.to_sql(COEFFICIENTS_TABLE_NAME, con=engine, if_exists="append")


def calculate_update_season_coefficient(statement, update_month: str) -> float:
    price_data = read_sql(sql=statement, con=engine)
    price_data["date"] = to_datetime(price_data["date"])
    price_data.set_index("date", inplace=True)
    print(price_data)
    coefficients_data = calculate_season_coefficients(price_data)
    print(coefficients_data)
    coefficient = coefficients_data.loc[update_month, "coefficient"]

    return coefficient


def parse_prices():
    if not is_data_in_db(PRICES_TABLE_NAME):
        quotes_data = prepare_data_frame()
        write_prices_to_db(quotes_data)
        coefficients_data = calculate_season_coefficients(quotes_data)
        write_coefficients_to_db(coefficients_data)
