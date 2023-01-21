
import asyncio
from collections import namedtuple
import logging
from common.svc.base_svc import BaseAsyncService
from common.constants import IndexerCancelReason, VideoVendor, VideoSource
from common.svc.config_db_svc import ConfigDBService, last_sync_tuple
from common.svc.video_catalog_db_svc import VideoCatalogDBService, record_tuple
from common.exceptions import APIClientWentBonkers, APIQuotaExpiredException, IndexerWentBonkers
from common.svc.video_vendor_svc import VideoVendorService, video_search_result, video_details
from datetime import datetime, timedelta, timezone

queue_record = namedtuple('VideoIngestionQueueRecord', 'video_id')

"""
Orchestrator responsible for the recurrent indexing of new video records
1. Uses Queue to handle ingestion rates between producer and consumer
2. 
"""
class VideoIndexerOrchestrator(BaseAsyncService):

    logger = logging.getLogger(__name__)

    def __init__(self, config_service, video_vendor, catalog_svc, search_query) -> None:
        self.config_svc: ConfigDBService = config_service
        self.video_vendor_svc: VideoVendorService = video_vendor
        self.vc_db_svc: VideoCatalogDBService = catalog_svc
        self.producer_stack = set()
        self.consumer_stack = set()
        self.Queue = asyncio.Queue()
        self.search_query = search_query
        self.cancel_reason = None

    async def init(self):
        pass

    async def terminate(self):
        pass

    def get(self):
        return self

    """
    Fetches video records from the vendor
    """
    async def fetch_videos(self):
        try:
            last_sync_time: last_sync_tuple = await self.config_svc.get_last_sync_time_for_vendor(VideoVendor.GOOGLE)
            self.logger.debug('last synct time %s', last_sync_time)
            await self.config_svc.upsert_last_sync_time_for_vendor(VideoVendor.GOOGLE, datetime.now(timezone.utc).replace(tzinfo=None))
            self.logger.debug('Updated last sync time %s', last_sync_time)
            async for record in self.video_vendor_svc.fetch_records(query=self.search_query, published_after=self._get_last_sync_time(last_sync_time)):
                self.logger.info("Producing some record %s", record)
                await self.Queue.put(
                    queue_record(record.video_id)
                )
        except APIQuotaExpiredException as e:
            self.logger.error('[fetch_videos] Quota expiry %s', e)
            # TODO: This is a very hacky way of handling quota expiry, need to move away from it
            self.cancel_reason = IndexerCancelReason.QUOTA_EXPIRY
            self.terminate_all_tasks()
        except Exception as e:
            self.logger.error('[fetch_videos] Something went wrong %s', e)
            self.terminate_all_tasks()

    """
    Upserts Video Records in the DB
    1. This method is idempotent so that we can handle duplicate ingestion of same video
    """
    async def handle_video_record(self, record: queue_record):
        try:
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
        except Exception as e:
            self.logger.error("[handle_video_record] Something went wrong while handling record %s", record.video_id)

    """
    Initialises Producer Coroutines, Adds new task every T sec
    """
    async def start_producer_stack(self):
        try:
            while(True):
                self.logger.error('Adding Producer')
                self.producer_stack.add(asyncio.create_task(self.fetch_videos()))
                # break
                await asyncio.sleep(20)
        except Exception as e:
            self.logger.error("[start_producer_stack] Caught some exception %s", str(e))

    """
    Consumer code which deques records from the queue and adds them to DB
    """
    async def consumer(self):
        while(True):
            q_record: queue_record = await self.Queue.get()
            self.logger.info("Consuming some record %s", q_record)
            await self.handle_video_record(q_record)
            self.Queue.task_done()
    
    """
    Initialises Consumer Stack
    counsumer_count - Number of Concurrent Consumers
    """
    async def start_consumer_stack(self, consumer_count: int):
        for i in range(consumer_count):
            self.logger.error('Adding Consumer %s', i)
            self.consumer_stack.add(asyncio.create_task(self.consumer()))
    

    """
    Orchestartes the whole whole between producers and consumers
    """
    async def orchestrate(self):
        try:
            self.logger.info('Orchestrating Indexer')
            producer_task = asyncio.create_task(self.start_producer_stack())
            await self.start_consumer_stack(1)
            await asyncio.gather(producer_task, *self.consumer_stack)
        except asyncio.CancelledError as e:
            self.logger.error("Something went wrong in orchestartor: %s and %s", self.cancel_reason, str(e))
            if self.cancel_reason == IndexerCancelReason.QUOTA_EXPIRY:
                await self.handle_quota_expiry()
    
    
    async def handle_quota_expiry(self):
        self.cancel_reason = None
        await self.video_vendor_svc.handle_quota_expiry()
        await self.orchestrate()
    
    
    """
    Terminates all Producers and Consumers for cleanup
    """
    def terminate_all_tasks(self):
        self.logger.error('I am terminating everything')
        for p in self.producer_stack:
            p.cancel()
        for c in self.consumer_stack:
            c.cancel()


    """
    Provides the last sync time for vendor
    If not provided then defaults to T-20sec
    """
    def _get_last_sync_time(self, last_sync: last_sync_tuple) -> datetime:
        if last_sync != None and last_sync.last_sync_time != None:
            return last_sync.last_sync_time
        else:
            return datetime.now(timezone.utc) - timedelta(seconds=20)

