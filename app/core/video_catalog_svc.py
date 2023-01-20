
from common.models import VideoCatalog, ContentDetails, VideoStatistics, VideoCatalogResponse, VideoCatalogSearchResponse, VideoSearchRequest
from common.svc.video_catalog_db_svc import VideoCatalogDBService, search_record_tuple, record_tuple, VideoCatalogSearchService
from common.constants import QueryType, SortOrder, PAGE_SIZE
from datetime import timedelta
from common.svc_registry import SvcRegistry
from common.svc.base_svc import ServiceKey

def transform_video_record(record: record_tuple) -> VideoCatalog:
    return VideoCatalog(
        video_id=record.video_id,
        title=record.title,
        description=record.description,
        published_at=int(round(record.published_at.timestamp())),
        published_at_str=str(record.published_at),
        thumbnails=record.thumbnails,
        duration_sec=record.duration_sec,
        duration_str=str(timedelta(seconds=record.duration_sec)),
        content_details=ContentDetails(
            privacy_status=record.privacy_status,
            definition=record.content_definition
        ),
        stats=VideoStatistics(
            views_count=record.views_count,
            likes_count=record.likes_count,
            favourite_count=record.favourite_count,
            comment_count=record.comment_count
        )
    )

def transform_video_search_record(record: search_record_tuple) -> VideoCatalog:
    return VideoCatalog(
        video_id=record.video_id,
        title=record.title,
        description=record.description,
        published_at=int(round(record.published_at.timestamp())),
        published_at_str=str(record.published_at),
        thumbnails=record.thumbnails,
        duration_sec=record.duration_sec,
        duration_str=str(timedelta(seconds=record.duration_sec)),
        content_details=ContentDetails(
            privacy_status=record.privacy_status,
            definition=record.content_definition
        ),
        stats=VideoStatistics(
            views_count=record.views_count,
            likes_count=record.likes_count,
            favourite_count=record.favourite_count,
            comment_count=record.comment_count
        )
    )


async def get_paginated_catalog(page: int, limit = PAGE_SIZE, sort_order: SortOrder = SortOrder.DESC) -> VideoCatalogResponse:
    vc_db_svc: VideoCatalogDBService = SvcRegistry.get_svc(ServiceKey.VC_DB_SVC)
    records = await vc_db_svc.get_records_by_published_date(offset=page*PAGE_SIZE, limit=limit, sort_order=sort_order)
    return VideoCatalogResponse(
        current_page=page,
        current_limit=limit,
        page_count=len(records),
        items=[transform_video_record(r) for r in records]
    )

async def search_video(request: VideoSearchRequest) -> VideoCatalogSearchResponse:
    vc_search_svc: VideoCatalogSearchService = SvcRegistry.get_svc(ServiceKey.VC_SEARCH_SVC)
    records = await vc_search_svc.search_catalog_by_title_and_description(
        q=request.query,
        type=_resolve_query_type(request),
        offset=request.page*PAGE_SIZE,
        limit=request.limit
    )
    return VideoCatalogSearchResponse(
        current_page=request.page,
        current_limit=request.limit,
        page_count=len(records),
        query=request.query,
        items=[transform_video_search_record(r) for r in records]
    )

def _resolve_query_type(request: VideoSearchRequest) -> QueryType:
    if request.is_phrase:
        return QueryType.PHRASE
    else:
        return QueryType.DEFAULT