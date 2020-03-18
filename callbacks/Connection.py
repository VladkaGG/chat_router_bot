from pymongo import MongoClient
from urllib.parse import urlparse
import logging
logger = logging.getLogger(__name__)


class ConnectionDB:
    connect = None
    host = None
    port = None
    user = None
    password = None
    database = None
    scheme = None

    def __init__(self, url: str = 'mongodb://127.0.0.1:27017/default') -> None:
        url = urlparse(url)
        self.scheme = url.scheme
        if self.scheme != 'mongodb':
            logger.error('В URI указана неверная схема')
        self.user = url.username
        self.password = url.password
        self.host = url.hostname
        self.port = url.port
        self.database = url.path[1]

    def __enter__(self) -> connect:
        try:
            self.connect = MongoClient('{}://{}:{}@{}:{}/{}'.format(self.scheme,
                                                                    self.user,
                                                                    self.password,
                                                                    self.host,
                                                                    self.port,
                                                                    self.database)) \
                if (self.user and self.password) else \
                MongoClient('{}://{}:{}/{}'.format(self.scheme, self.host, self.port, self.database))
            return self.connect
        except ConnectionError:
            logger.error('Проблемы подключения к БД')
            return None

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type and self.connect:
            logging.error(f"Exception occurred\n{exc_tb}\n{exc_type}: {exc_val}")
            self.connect.close()
            self.connect = None
            return None
        elif exc_type and not self.connect:
            logging.error(f"Exception occurred\n{exc_tb}\n{exc_type}: {exc_val}")
            return None
        self.connect.close()
        return None