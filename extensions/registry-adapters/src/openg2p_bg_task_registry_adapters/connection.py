"""Decode a register's connection string into the settings its connector needs.

db:  postgresql://user:pass@host:5432/dbname
dci: http(s)://host[:port]/search/path?reg_type=..&reg_record_type=..&timeout=30&ssl_verify=true
     The URL without the query is the endpoint searched, e.g.
     http://farmer-registry-partner-api/dci/sync/search.

Standard library only, so it can be tested without the adapter dependencies.
"""

from dataclasses import dataclass, field
from urllib.parse import parse_qs, quote, unquote, urlsplit, urlunsplit

CONNECTORS = ("db", "dci")
DCI_PARAMS = ("reg_type", "reg_record_type", "timeout", "ssl_verify")


class RegistryConnectionError(ValueError):
    pass


@dataclass(frozen=True)
class RegistryConnection:
    register: str
    connector: str

    db_driver: str = "postgresql"
    db_username: str = ""
    db_password: str = field(default="", repr=False)
    db_hostname: str = ""
    db_port: int = 5432
    db_dbname: str = ""

    search_url: str = ""
    partner_api_timeout: int = 30
    partner_api_ssl_verify: bool = True
    reg_type: str = ""
    reg_record_type: str = ""

    @classmethod
    def parse(
        cls,
        register: str,
        connector: str,
        connection_string: str,
        reg_type: str = "",
        reg_record_type: str = "",
    ) -> "RegistryConnection":
        value = (connection_string or "").strip()
        if not value:
            raise RegistryConnectionError(
                f"Register '{register}' is not configured: set "
                f"REGISTRY_ADAPTERS_{register.upper()}_CONNECTION_STRING."
            )
        connector = (connector or "").strip().lower()
        if connector not in CONNECTORS:
            raise RegistryConnectionError(
                f"Register '{register}': connector must be db or dci, "
                f"got '{connector}'."
            )
        parts = urlsplit(value)
        if not parts.scheme or not parts.hostname:
            raise RegistryConnectionError(
                f"Register '{register}': connection string is not a URL."
            )
        try:
            port = parts.port
        except ValueError as exc:
            raise RegistryConnectionError(
                f"Register '{register}': invalid port in connection string."
            ) from exc
        if connector == "db":
            return cls._db(register, parts, port)
        return cls._dci(register, parts, reg_type, reg_record_type)

    @classmethod
    def _db(cls, register, parts, port) -> "RegistryConnection":
        dbname = unquote(parts.path.lstrip("/"))
        if not dbname:
            raise RegistryConnectionError(
                f"Register '{register}': db connection string has no database name."
            )
        return cls(
            register=register,
            connector="db",
            db_driver=parts.scheme,
            db_username=unquote(parts.username or ""),
            db_password=unquote(parts.password or ""),
            db_hostname=parts.hostname,
            db_port=port or 5432,
            db_dbname=dbname,
        )

    @classmethod
    def _dci(cls, register, parts, reg_type, reg_record_type) -> "RegistryConnection":
        if parts.scheme not in ("http", "https"):
            raise RegistryConnectionError(
                f"Register '{register}': dci connection string must be http or https."
            )
        params = {key: values[-1] for key, values in parse_qs(parts.query).items()}
        unknown = sorted(set(params) - set(DCI_PARAMS))
        if unknown:
            raise RegistryConnectionError(
                f"Register '{register}': unknown dci parameter(s) {unknown}; "
                f"expected {list(DCI_PARAMS)}."
            )
        path = parts.path.rstrip("/")
        if not path:
            raise RegistryConnectionError(
                f"Register '{register}': dci connection string must be the full "
                f"search URL, e.g. {parts.scheme}://{parts.netloc}/dci/sync/search."
            )
        return cls(
            register=register,
            connector="dci",
            search_url=urlunsplit((parts.scheme, parts.netloc, path, "", "")),
            partner_api_timeout=_positive_int(register, params.get("timeout", "30")),
            partner_api_ssl_verify=_bool(register, params.get("ssl_verify", "true")),
            reg_type=params.get("reg_type") or reg_type,
            reg_record_type=params.get("reg_record_type") or reg_record_type,
        )

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
            f"{driver}://{quote(self.db_username, safe='')}:"
            f"{quote(self.db_password, safe='')}"
            f"@{self.db_hostname}:{self.db_port}/{self.db_dbname}"
        )


def _positive_int(register: str, value: str) -> int:
    try:
        number = int(value)
    except ValueError:
        number = 0
    if number <= 0:
        raise RegistryConnectionError(
            f"Register '{register}': timeout must be a positive integer, got '{value}'."
        )
    return number


def _bool(register: str, value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in ("true", "1", "yes"):
        return True
    if lowered in ("false", "0", "no"):
        return False
    raise RegistryConnectionError(
        f"Register '{register}': ssl_verify must be true or false, got '{value}'."
    )
