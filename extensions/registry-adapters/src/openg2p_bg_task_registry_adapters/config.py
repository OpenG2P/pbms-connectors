from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class RegistryAdapterSettings(BaseSettings):
    """Registry transport settings. Read by the factory and the four computations.

    Env prefix is ``registry_adapters_``. Celery workers and the staff portal
    set the same variables; they do not open a registry database themselves.
    """

    model_config = SettingsConfigDict(
        env_prefix="registry_adapters_",
        env_file=".env",
        extra="ignore",
    )

    connector: Literal["db", "dci"] = "db"

    db_driver: str = "postgresql"
    db_username: str = "postgres"
    db_password: str = "postgres"
    db_hostname: str = "localhost"
    db_port: int = 5432
    db_dbname: str = "socialregistrydb"

    partner_api_url: str = "http://localhost:8000"
    partner_api_timeout: int = 30
    partner_api_ssl_verify: bool = True
    farmer_reg_type: str = "Farmer"
    household_reg_type: str = "Household"
    farmer_reg_record_type: str = "Farmer"
    household_reg_record_type: str = "Household"

    @classmethod
    def get_config(cls) -> "RegistryAdapterSettings":
        return cls()

    def sync_url(self) -> str:
        driver = self.db_driver
        if driver.endswith("+asyncpg"):
            driver = driver.replace("+asyncpg", "")
        return self._url(driver)

    def async_url(self) -> str:
        driver = self.db_driver
        if not driver.endswith("+asyncpg"):
            driver = f"{driver.split('+', 1)[0]}+asyncpg"
        return self._url(driver)

    def _url(self, driver: str) -> str:
        return (
            f"{driver}://{self.db_username}:{self.db_password}"
            f"@{self.db_hostname}:{self.db_port}/{self.db_dbname}"
        )
