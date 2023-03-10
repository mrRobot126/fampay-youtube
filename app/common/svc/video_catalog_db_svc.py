from abc import ABC, abstractmethod
from collections import namedtuple
from typing import List

from common.constants import QueryType, SortOrder

record_tuple = namedtuple('VideoRecordTuple', 'source video_id title description thumbnails duration_sec likes_count views_count comment_count favourite_count privacy_status published_at content_definition')
search_record_tuple = namedtuple('VideoSearchTuple', 'source video_id title description thumbnails duration_sec likes_count views_count comment_count favourite_count privacy_status published_at content_definition')

"""
Skeleton for Video Catalog DB Service
Provides methods which can be implemented later by any kind of persistmence layers Eg postgresql, mongodb etc
"""
class VideoCatalogDBService(ABC):
    
    @abstractmethod
    async def upsert_video_record(self, record: record_tuple) -> int:
        pass

    @abstractmethod
    async def get_video_record_by_video_id(self, video_id: str) -> record_tuple:
        pass

    @abstractmethod
    async def get_records_by_published_date(self, offset: int, limit: int, sort_order: SortOrder) -> List[record_tuple]:
        pass


"""
Skeleton for Video Catalog Search Service
Provides methods which can be implemented later by any kind of search solution layers Eg postgresql, elasticsearch, solr etc
"""
class VideoCatalogSearchService(ABC):

    @abstractmethod
    async def search_catalog_by_title_and_description(self, q: str, type: QueryType, offset: int, limit: int) -> List[search_record_tuple]:
        pass