from collections import namedtuple
from datetime import datetime
import json
import logging
from typing import List

from common.exceptions import APIClientWentBonkers, IndexerWentBonkers
from common.exceptions import APIQuotaExpiredException
from common.constants import AuthStatus, VideoSource, VideoVendor, AuthMethod
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
    
    def __init__(self, config_db_svc, vendor: VideoVendor, auth_method: AuthMethod) -> None:
        self.config_svc: ConfigDBService = config_db_svc
        self.vendor: VideoVendor = vendor
        self.auth_method:AuthMethod = auth_method

    async def terminate(self):
        pass

    def get(self):
        return self


    async def init(self):
        auth_records: List[auth_record] = await self.config_svc.get_record_for_vendor_and_method_and_status(self.vendor, self.auth_method, AuthStatus.ACTIVE)
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
            raise APIClientWentBonkers(self.vendor)


    async def fetch_records(self, query: str, published_after: datetime, order: str = 'date', region_code: str = 'IN', relevance_language: str = 'en'):
        nextPageToken = None
        try:
            while(True):
                search_response = self.client.search().list(
                        q = query,
                        part = 'id,snippet',
                        fields = 'items(id, snippet(publishedAt)),pageInfo,nextPageToken',
                        order = order,
                        type = 'video',
                        publishedAfter = self._get_google_datetime_format(published_after),
                        pageToken = nextPageToken
                    ).execute()
                
                for search_result in search_response.get('items', []):
                    yield video_search_result(search_result['id']['videoId'], search_result['snippet']['publishedAt'])
                
                nextPageToken = search_response.get('nextPageToken', None)
                if (nextPageToken is None):
                    self.logger.error("I am breaking coz no page token")
                    break
                self.logger.error("Got new page token bitches: %s", nextPageToken)
        except HttpError as e:
                reason: str = json.loads(e.content).get('error').get('errors')[0].get('reason')
                if e.resp.status in [403]:
                    self.logger.error('Having some trouble getting the data %s and %s', reason, e)
                    if (reason.lower() == 'quotaExceeded'.lower()):
                        raise APIQuotaExpiredException()
                else:
                    self.logger.error('Having some trouble getting the data %s and %s', reason, e)
                    raise APIClientWentBonkers(VideoVendor.GOOGLE.value)
        except Exception as e:
            self.logger.error("[fetch_records] Something went wrong: %s", str(e))
            raise IndexerWentBonkers()
            
    
    async def fetch_record_details(self, video_id: str) -> video_details:
        video_response_list = self.client.videos().list(
            part = 'snippet,contentDetails,statistics,status',
            fields = 'items(snippet(publishedAt, title, description, thumbnails, channelTitle),contentDetails(duration, definition),status(privacyStatus),statistics)',
            id = video_id
        ).execute().get('items', [])

        if video_response_list:
            record = video_response_list[0]
            return video_details(
                VideoSource.YOUTUBE.value,
                video_id,
                record['snippet']['title'],
                record['snippet'].get('description', ''),
                record['snippet'].get('thumbnails', []),
                self._parse_iso_timestamp(record['snippet']['publishedAt']),
                self._parse_iso_duration_to_seconds(record['contentDetails']['duration']),
                record['contentDetails']['definition'],
                record['status']['privacyStatus'],
                int(record['statistics'].get('viewCount', 0)),
                int(record['statistics'].get('likeCount', 0)),
                int(record['statistics'].get('favoriteCount', 0)),
                int(record['statistics'].get('commentCount', 0))
            )
        else:
            return None

    async def handle_quota_expiry(self):
        self.logger.error("I am handling quota expiry %s, %s", self.vendor, self.auth_method)
        auth_records: List[auth_record] = await self.config_svc.get_record_for_vendor_and_method_and_status(self.vendor, self.auth_method, AuthStatus.ACTIVE)
        self.logger.error("I am handling quota expiry %s", auth_records)
        if len(auth_records) > 0:
            record_id = auth_records[0].id
            self.logger.error("Updating status of expired key: %s", record_id)
            await self.config_svc.update_auth_status(record_id, AuthStatus.QUOTA_EXCEEDED)
        eligible_records: List[auth_record] = await self.config_svc.get_record_for_vendor_and_method_and_status(self.vendor, self.auth_method, AuthStatus.ELIGIBLE)
        if (len(eligible_records) == 0):
            raise Exception("No Eligible Auth records for vendor: {} and method: {}".format(self.vendor, self.auth_method))
        elected_record = self._elect_eligible_record(eligible_records)
        self.logger.error("Updating status of elected key: %s", elected_record.id)
        await self.config_svc.update_auth_status(elected_record.id, AuthStatus.ACTIVE)
        await self._reinitalise_build()
        
    def _elect_eligible_record(self, records: List[auth_record]) -> auth_record:
        self.logger.error("All eligible records %s", records)
        return records[0]
    
    async def _reinitalise_build(self):
        self.logger.error("Reinitiating Build")
        await self.init()
    
    def _parse_iso_duration_to_seconds(self, iso_date: str) -> int:
        return int(parse_iso_duration(iso_date).total_seconds())

    def _parse_iso_timestamp(self, iso_date: str) -> datetime:
        return datetime.fromisoformat(iso_date.replace("Z", "+00:00")).replace(tzinfo=None)

    def _get_google_datetime_format(self, date: datetime) -> str:
        format = date.strftime("%Y-%m-%dT%H:%M:%S") + 'Z'
        self.logger.error("I am published after format %s for datetime %s", format, date.timestamp())
        return format


