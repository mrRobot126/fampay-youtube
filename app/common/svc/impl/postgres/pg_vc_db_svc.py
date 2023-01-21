from ast import List
import json
import logging
from common.constants import SortOrder
from common.svc.base_svc import BaseAsyncService
from common.svc.db_conn_svc import DatabaseConnectionPoolSvc
from common.svc.video_catalog_db_svc import VideoCatalogDBService, record_tuple


class PostgresVideoCatalogDBService(BaseAsyncService, VideoCatalogDBService):

    logger = logging.getLogger(__name__)

    def __init__(self, conn_svc) -> None:
        self.conn_svc: DatabaseConnectionPoolSvc = conn_svc

    async def init(self):
        self.conn: DatabaseConnectionPoolSvc = self.conn_svc.get()

    async def terminate(self):
        pass

    def get(self):
        return self


    async def upsert_video_record(self, record: record_tuple):
        result = await self.conn.fetchrow(
            """
                INSERT INTO video_catalog AS vc 
                (source, video_id, title, description, thumbnails, published_at, duration_sec, content_definition, privacy_status, views_count, like_count, favourite_count, comment_count) 
                VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                ON CONFLICT(video_id)
                DO UPDATE SET 
                title = excluded.title, 
                description = excluded.description, 
                privacy_status = excluded.privacy_status, 
                views_count = GREATEST(excluded.views_count, vc.views_count),
                like_count = GREATEST(excluded.like_count, vc.like_count),
                favourite_count = GREATEST(excluded.favourite_count, vc.favourite_count),
                comment_count = GREATEST(excluded.comment_count, vc.comment_count)
                RETURNING *, CASE WHEN xmax::text::int > 0 THEN false ELSE true END AS is_insert
            """,
            record.source,
            record.video_id,
            record.title,
            record.description,
            json.dumps(record.thumbnails),
            record.published_at,
            record.duration_sec,
            record.content_definition,
            record.privacy_status,
            record.views_count,
            record.likes_count,
            record.favourite_count,
            record.comment_count
        )
        return result['id']

    async def get_video_record_by_video_id(self, video_id: str) -> record_tuple:
        record = await self.conn.fetchrow(
            """
                SELECT 
                    vc.source,
                    vc.video_id,
                    vc.title,
                    vc.description,
                    vc.thumbnails,
                    vc.duration_sec,
                    vc.like_count,
                    vc.views_count,
                    vc.comment_count,
                    vc.favourite_count,
                    vc.privacy_status,
                    vc.published_at,
                    vc.content_definition
                FROM video_catalog vc WHERE vc.video_id = $1
            """,
            video_id
        )
        if record == None:
            return None
        return self._parse_video_record(record)


    async def get_records_by_published_date(self, offset: int, limit: int, sort_order: SortOrder):
        self.logger.error('%s %s %s', offset, limit, sort_order)
        records = await self.conn.fetch("""
            SELECT
                vc.source,
                vc.video_id,
                vc.title,
                vc.description,
                vc.thumbnails,
                vc.duration_sec,
                vc.like_count,
                vc.views_count,
                vc.comment_count,
                vc.favourite_count,
                vc.privacy_status,
                vc.published_at,
                vc.content_definition
            FROM video_catalog vc
            ORDER BY vc.published_at desc
            OFFSET $1
            LIMIT $2
        """,
        offset,
        limit
        )

        if (records):
            return [self._parse_video_record(r) for r in records]
        else:
            return []

    def _parse_video_record(self, record) -> record_tuple:
        if record == None:
            return None
        return record_tuple(
            source=record['source'],
            video_id=record['video_id'],
            title=record['title'],
            description=record['description'],
            thumbnails=json.loads(record['thumbnails']),
            duration_sec=record['duration_sec'],
            likes_count=record['like_count'],
            views_count=record['views_count'],
            comment_count=record['comment_count'],
            favourite_count=record['favourite_count'],
            privacy_status=record['privacy_status'],
            published_at=record['published_at'],
            content_definition=record['content_definition']
        )