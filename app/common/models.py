## This file contains all req-response models

from typing import List, Union, Optional, Any
from pydantic import BaseModel
from common.constants import QueryType, SortOrder, PAGE_SIZE



class ContentDetails(BaseModel):
    privacy_status: str
    definition: str

class VideoStatistics(BaseModel):
    views_count: int = 0
    likes_count: int = 0
    favourite_count: int = 0
    comment_count: int = 0

class VideoCatalog(BaseModel):
    video_id: str
    title: str
    description: Optional[str]
    thumbnails: Any
    published_at: int
    published_at_str: str
    duration_sec: int
    duration_str: str
    content_details: ContentDetails
    stats: VideoStatistics
    

class VideoCatalogRequest(BaseModel):
    sort_order: Optional[str] = SortOrder.DESC
    page: int = 0
    count: int = PAGE_SIZE

class VideoCatalogResponse(BaseModel):
    current_page: int
    page_count: int
    items: List[VideoCatalog]


class VideoSearchRequest(BaseModel):
    query: str
    is_phrase: bool
    page: int
    limit: int = PAGE_SIZE

class VideoCatalogSearchResponse(BaseModel):
    query: str
    page_count: int
    items: List[VideoCatalog]
