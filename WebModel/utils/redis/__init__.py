from WebModel.utils.redis.client import Redis, StrictRedis
from WebModel.utils.redis.connection import (
    BlockingConnectionPool,
    ConnectionPool,
    Connection,
    SSLConnection,
    UnixDomainSocketConnection
)
from WebModel.utils.redis.utils import from_url
from WebModel.utils.redis.exceptions import (
    AuthenticationError,
    BusyLoadingError,
    ConnectionError,
    DataError,
    InvalidResponse,
    PubSubError,
    ReadOnlyError,
    RedisError,
    ResponseError,
    TimeoutError,
    WatchError
)


__version__ = '2.10.3'
VERSION = tuple(map(int, __version__.split('.')))

__all__ = [
    'Redis', 'StrictRedis', 'ConnectionPool', 'BlockingConnectionPool',
    'Connection', 'SSLConnection', 'UnixDomainSocketConnection', 'from_url',
    'AuthenticationError', 'BusyLoadingError', 'ConnectionError', 'DataError',
    'InvalidResponse', 'PubSubError', 'ReadOnlyError', 'RedisError',
    'ResponseError', 'TimeoutError', 'WatchError'
]
