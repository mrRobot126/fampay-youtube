import enum
from abc import ABC, abstractmethod


class ServiceKey(enum.Enum):
    YOUTUBE_API_SVC = 1
    DB_CONN = 2
    INDEXER_DB_SVC = 3
    DB_SVC = 4

class BaseAsyncService(ABC):

    @abstractmethod
    async def init(self):
        pass

    async def terminate(self):
        pass

    @abstractmethod
    def get(self):
        pass