from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from .connection import RegistryConnection


class RegisterSettings(BaseSettings):
    """Connector and connection string of one register.

    Built per register with ``_env_prefix=f"registry_adapters_{register}_"``,
    so each register reads REGISTRY_ADAPTERS_<REGISTER>_CONNECTOR and
    REGISTRY_ADAPTERS_<REGISTER>_CONNECTION_STRING. Celery workers and the
    staff portal set the same variables.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    connector: str = ""
    connection_string: str = ""


@lru_cache
def get_connection(
    register: str, reg_type: str = "", reg_record_type: str = ""
) -> RegistryConnection:
    settings = RegisterSettings(_env_prefix=f"registry_adapters_{register}_")
    return RegistryConnection.parse(
        register,
        settings.connector,
        settings.connection_string,
        reg_type,
        reg_record_type,
    )
