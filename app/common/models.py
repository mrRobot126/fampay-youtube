import datetime
from typing import List
from pyparsing import Optional
from pydantic import BaseModel


class ChannelDetails(BaseModel):
    channel_title: str

class ContentDetails(BaseModel):
    privacy_status: str
    definition: str

class VideoStatistics(BaseModel):
    views_count: int
    likes_count: int
    favourite_count: int
    comment_count: int

class VideoCatalog(BaseModel):
    video_id: str
    title: str
    description: Optional[str]
    channel_details: ChannelDetails
    published_at: datetime
    duration: int
    duration_str: str
    content_details: ContentDetails
    stats: VideoStatistics
    

class VideoCatalogRequest(BaseModel):
    sort_order: str = "desc"
    page: int
    count: int

class VideoCatalogResponse(BaseModel):
    current_page: int
    page_count: int
    items: List[VideoCatalog]


class VideoSearchRequest(BaseModel):
    query: str
    count: int

class VideoSearchResponse(BaseModel):
    query: str
    count: int
    items: List[VideoCatalog]
