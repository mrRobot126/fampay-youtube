
from common.svc.config_db_svc import ConfigDBService, last_sync_tuple
from common.svc.video_catalog_db_svc import VideoCatalogDBService, record_tuple
from common.svc.video_vendor_svc import VideoVendorService, video_search_result, video_details
from common.svc_registry import SvcRegistry
from common.svc.base_svc import ServiceKey
from datetime import datetime, timedelta


class VideoIndexer():

    def __init__(self) -> None:
        self.config_svc: ConfigDBService = SvcRegistry.get_svc(ServiceKey.CONFIG_SVC)
        self.video_vendor_svc: VideoVendorService = SvcRegistry.get_svc(ServiceKey.VIDEO_VENDOR_SVC)
        self.vc_db_svc: VideoCatalogDBService = SvcRegistry.get_svc(ServiceKey.VC_DB_SVC)

    async def fetch_videos(self):
        last_sync_time: last_sync_tuple = await self.config_svc.get_last_sync_time_for_vendor('youtube')
        async for record in self.video_vendor_svc.fetch_records(query="football", published_after=self._get_last_sync_time(last_sync_time)):
            await self.handle_video_record(record)

    async def handle_video_record(self, record: video_search_result):
        video_record: video_details = await self.video_vendor_svc.fetch_record_details(record.video_id)
        await self.vc_db_svc.upsert_video_record(
            record_tuple(
                source = video_record.source,
                video_id = video_record.video_id,
                title = video_record.title,
                description= video_record.description,
                thumbnails = video_record.thumbnails,
                duration_sec = video_record.duration_sec,
                likes_count = video_record.like_count,
                views_count = video_record.views_count,
                comment_count = video_record.comment_count,
                favourite_count = video_record.favourite_count,
                privacy_status = video_record.privacy_status,
                published_at = video_record.published_at,
                content_definition = video_record.content_definition
            )
        )

    def _get_last_sync_time(self, last_sync: last_sync_tuple) -> datetime:
        if last_sync != None and last_sync.last_sync_time != None:
            return last_sync.last_sync_time
        else:
            return datetime.now() - timedelta(minutes=10)

