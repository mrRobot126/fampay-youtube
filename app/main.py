import asyncio
import logging
from mmap import PAGESIZE
import sys
from common.svc.base_svc import ServiceKey
from core.video_catalog_svc import get_paginated_catalog, search_video
from common.models import VideoCatalogSearchResponse, VideoCatalogResponse, VideoCatalogRequest, VideoSearchRequest
from common.svc_registry import SvcRegistry
from common.constants import IndexerCancelReason
from core.indexer import VideoIndexerOrchestrator
from fastapi import FastAPI
import signal
from common.constants import SortOrder, PAGE_SIZE
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

logging.basicConfig(level=logging.INFO)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

"""
Orchestartes cleanups all coroutines on termination / exit signal
"""
def receive_signal(signalNumber, frame):
    cleanup_couroutines()
    sys.exit()


def cleanup_couroutines():
    indexer: VideoIndexerOrchestrator = SvcRegistry.get_svc(ServiceKey.VIDEO_INDEXER_SVC)
    indexer.terminate_all_tasks()
    for t in asyncio.all_tasks():
        t.cancel()


"""
Application Startup Logic
1. Initialise Service Registry
2. Start the Indexer Orchestrator
3. Reads config from the environment
"""
@app.on_event("startup")
async def startup():
    svc_registry = SvcRegistry(
        {
            "db_conn": "postgresql://postgres:secret@127.0.0.1:6000/fampay",
            "query": "football"
        }
    )
    await svc_registry.initialise()
    indexer: VideoIndexerOrchestrator = SvcRegistry.get_svc(ServiceKey.VIDEO_INDEXER_SVC)
    signal.signal(signal.SIGINT, receive_signal)
    asyncio.create_task(indexer.orchestrate())


"""
GET API - Search Video Records by Query
query -> search query
page -> current page number
limit -> number of results required
is_phrase -> whether to treat query as a phrase or not ie order of words matter or not
"""
@app.get("/search", response_model=VideoCatalogSearchResponse)
async def get_search_response(query: str, page: int = 0, limit: int = PAGE_SIZE, is_phrase: bool = False):
    return await search_video(
        request=VideoSearchRequest(
            query=query,
            page=page,
            limit=limit,
            is_phrase=is_phrase
        )
    )


"""
GET API - Paginated Response of Video Catalog
page -> current page number
limit -> number of results required
sort_order -> Sorting order of search results
"""
@app.get("/list", response_model=VideoCatalogResponse)
async def list_videos(page: int = 0, limit: int = PAGE_SIZE, sort_order: SortOrder = SortOrder.DESC):
    return await get_paginated_catalog(page=page, limit=limit, sort_order=sort_order)