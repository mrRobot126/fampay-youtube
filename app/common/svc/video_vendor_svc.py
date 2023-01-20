from datetime import datetime
import logging
from typing import List
from app.common.constants import AuthStatus
from app.common.svc.config_db_svc import ConfigDBService, auth_record
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class VideoVendorService():

    logger = logging.getLogger(__name__)

    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'
    
    def __init__(self, config_db_svc) -> None:
        self.config_svc: ConfigDBService = config_db_svc


    async def initialise(self):
        auth_records: List[auth_record] = await self.config_svc.get_record_for_vendor_and_method_and_status('google', 'auth_token', AuthStatus.ACTIVE)
        if len(auth_records) == 0:
            self.logger.error('[VideoVendorService][initialise] No Active Auth Record Found')
        authtoken = auth_record[0]['token']
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
            order = order,
            type = 'video',
            publishedAfter = published_after.isoformat("T") + "Z",
            relevanceLanguage = 'en',
            regionCode = 'IN'
        ).execute()

        for search_result in search_response.get('items', []):
            yield search_result


