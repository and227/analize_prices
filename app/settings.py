from pydantic import BaseSettings


class Settings(BaseSettings):
    INPUT_FILE_NAME: str = "KC-057.CSV"


settings = Settings()
