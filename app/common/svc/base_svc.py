import enum
from abc import ABC, abstractmethod


class ServiceKey(enum.Enum):
    YOUTUBE_API_SVC = 1
    DB_CONN = 2
    VC_SEARCH_SVC = 3
    VC_DB_SVC = 4
    CONFIG_SVC = 5
    VIDEO_VENDOR_SVC = 6

class BaseAsyncService(ABC):

    @abstractmethod
    async def init(self):
        pass

    async def terminate(self):
        pass

    @abstractmethod
    def get(self):
        pass