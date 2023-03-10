import json
import logging
from typing import List
from common.constants import QueryType
from common.svc.base_svc import BaseAsyncService
from common.svc.db_conn_svc import DatabaseConnectionPoolSvc
from common.svc.video_catalog_db_svc import VideoCatalogSearchService, search_record_tuple
from common.constants import AuthStatus


"""
Postgresql Implementation of VideoCatalogSearchService
"""
class PostgresVCSearchService(BaseAsyncService, VideoCatalogSearchService):

    logger = logging.getLogger(__name__)

    def __init__(self, conn_svc) -> None:
        self.conn_svc: DatabaseConnectionPoolSvc = conn_svc

    async def init(self):
        self.conn: DatabaseConnectionPoolSvc = self.conn_svc.get()

    async def terminate(self):
        pass

    def get(self):
        return self

    """
    Search Video Catalog by Title And Descripiton
    1. Handles if the Query is a phrase or not ie word order matters or not
    """
    async def search_catalog_by_title_and_description(self, q: str, type: QueryType, offset: int = 0, limit: int = 20) -> List[search_record_tuple]:
        if type == QueryType.PHRASE:
            records = await self.conn.fetch(
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
                    FROM video_catalog vc
                    WHERE vc.ts_title @@ phraseto_tsquery('english', $1)
                    ORDER BY vc.published_at DESC
                    OFFSET $2
                    LIMIT $3
                """,
                q,
                offset,
                limit
            )
            return self._process_search_records(records)
        else:
            processed_query = ' & '.join(q.split(' '))
            records = await self.conn.fetch(
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
                    FROM video_catalog vc
                    WHERE vc.ts_title @@ phraseto_tsquery('english', $1)
                    ORDER BY vc.published_at DESC
                    OFFSET $2
                    LIMIT $3
                """,
                '**{}**'.format(processed_query),
                offset,
                limit
            )
            return self._process_search_records(records)

    def _process_search_records(self, records) -> List[search_record_tuple]:
        if records:
            return [
                self._parse_search_video_record(r) for r in records
            ]
        else:
            return []

    def _parse_search_video_record(self, record) -> search_record_tuple:
        if record == None:
            return None
        return search_record_tuple(
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