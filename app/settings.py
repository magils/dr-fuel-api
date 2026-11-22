from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    enviroment: str = "local"
    db_host: str
    db_port: int = 3306
    db_username: str = ""
    db_password: str = ""
    db_name: str
    app_port: int = 8000
    db_vendor_connection_prefix: str = "postgresql+psycopg"

    @property
    def db_connection_url(self):
        return f"{self.db_vendor_connection_prefix}://{self.db_username}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = Settings()