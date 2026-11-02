from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from .config import RegistryAdapterSettings

_sync_engine = None
_async_engine = None


def sync_session():
    global _sync_engine
    if _sync_engine is None:
        settings = RegistryAdapterSettings.get_config()
        _sync_engine = create_engine(settings.sync_url(), poolclass=NullPool)
    return sessionmaker(bind=_sync_engine, expire_on_commit=False)()


def async_session():
    global _async_engine
    if _async_engine is None:
        settings = RegistryAdapterSettings.get_config()
        _async_engine = create_async_engine(settings.async_url(), poolclass=NullPool)
    return async_sessionmaker(bind=_async_engine, expire_on_commit=False)()
