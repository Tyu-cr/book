from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    db_session: SecretStr
    secret_key_flask: SecretStr
    google_api_key: SecretStr

    class Config:
        env_file = '../.env'
        env_file_encoding = 'utf-8'


config = Config()
