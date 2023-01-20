from collections import namedtuple
from datetime import datetime
import logging
from typing import List
from common.constants import AuthStatus
from common.svc.base_svc import BaseAsyncService
from common.utils import parse_iso_duration
from common.svc.config_db_svc import ConfigDBService, auth_record
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

video_search_result = namedtuple('VideoSearchResult', 'video_id published_at')
video_details = namedtuple('VideoDetails', 'source video_id title description thumbnails published_at duration_sec content_definition privacy_status views_count like_count comment_count favourite_count')

class VideoVendorService(BaseAsyncService):

    logger = logging.getLogger(__name__)

    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'
    
    def __init__(self, config_db_svc) -> None:
        self.config_svc: ConfigDBService = config_db_svc

    async def terminate(self):
        pass

    def get(self):
        return self


    async def init(self):
        auth_records: List[auth_record] = await self.config_svc.get_record_for_vendor_and_method_and_status('google', 'auth_token', AuthStatus.ACTIVE)
        if len(auth_records) == 0:
            self.logger.error('[VideoVendorService][initialise] No Active Auth Record Found')
        authtoken = auth_records[0].config['auth_token']
        try:
            self.client = build(
                self.YOUTUBE_API_SERVICE_NAME, 
                self.YOUTUBE_API_VERSION,
                developerKey=authtoken
            )
        except HttpError as e:
            self.logger.error('[VideoVendorService][initialise] Something went wrong in client initialisation')


    async def fetch_records(self, query: str, published_after: datetime, order: str = 'date', region_code: str = 'IN', relevance_language: str = 'en'):
        search_response = self.client.search().list(
            q = query,
            part = 'id,snippet',
            fields = 'items(id, snippet(publishedAt))',
            order = order,
            type = 'video',
            publishedAfter = published_after.isoformat("T") + "Z",
            relevanceLanguage = 'en',
            regionCode = 'IN'
        ).execute()

        for search_result in search_response.get('items', []):
            yield video_search_result(search_result['id']['videoId'], search_result['snippet']['publishedAt'])
    
    async def fetch_record_details(self, video_id: str) -> video_details:
        video_response_list = self.client.videos().list(
            part = 'snippet,contentDetails,statistics,status',
            fields = 'items(snippet(publishedAt, title, description, thumbnails, channelTitle),contentDetails(duration, definition),status(privacyStatus),statistics)',
            id = video_id
        ).execute().get('items', [])

        if video_response_list:
            record = video_response_list[0]
            return video_details(
                'youtube',
                video_id,
                record['snippet']['title'],
                record['snippet']['description'],
                record['snippet']['thumbnails'],
                self._parse_iso_timestamp(record['snippet']['publishedAt']),
                self._parse_iso_duration_to_seconds(record['contentDetails']['duration']),
                record['contentDetails']['definition'],
                record['status']['privacyStatus'],
                int(record['statistics']['viewCount']),
                int(record['statistics']['likeCount']),
                int(record['statistics']['favoriteCount']),
                int(record['statistics']['commentCount']),
            )
        else:
            return None
    
    def _parse_iso_duration_to_seconds(self, iso_date: str) -> int:
        return int(parse_iso_duration(iso_date).total_seconds())

    def _parse_iso_timestamp(self, iso_date: str) -> datetime:
        return datetime.fromisoformat(iso_date.replace("Z", "+00:00")).replace(tzinfo=None)
    


