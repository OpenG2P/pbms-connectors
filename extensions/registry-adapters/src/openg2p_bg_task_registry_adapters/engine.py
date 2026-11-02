from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from .connection import RegistryConnection

_sync_engines = {}
_async_engines = {}


def sync_session(connection: RegistryConnection):
    url = connection.sync_url()
    if url not in _sync_engines:
        _sync_engines[url] = create_engine(url, poolclass=NullPool)
    return sessionmaker(bind=_sync_engines[url], expire_on_commit=False)()


def async_session(connection: RegistryConnection):
    url = connection.async_url()
    if url not in _async_engines:
        _async_engines[url] = create_async_engine(url, poolclass=NullPool)
    return async_sessionmaker(bind=_async_engines[url], expire_on_commit=False)()
