import asyncio
import sys
from common.svc.base_svc import ServiceKey
from core.video_catalog_svc import get_paginated_catalog, search_video
from common.models import VideoCatalogSearchResponse, VideoCatalogResponse, VideoCatalogRequest, VideoSearchRequest
from common.svc_registry import SvcRegistry
from common.constants import IndexerCancelReason
from core.indexer import VideoIndexerOrchestrator
from fastapi import FastAPI
import signal
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def receive_signal(signalNumber, frame):
    cleanup_couroutines()
    sys.exit()

def cleanup_couroutines():
    indexer: VideoIndexerOrchestrator = SvcRegistry.get_svc(ServiceKey.VIDEO_INDEXER_SVC)
    indexer.terminate_all_tasks()
    for t in asyncio.all_tasks():
        t.cancel()

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


@app.post("/search", response_model=VideoCatalogSearchResponse)
async def get_search_response(request: VideoSearchRequest):
    return await search_video(request=request)

@app.post("/list", response_model=VideoCatalogResponse)
async def list_videos(request: VideoCatalogRequest):
    return await get_paginated_catalog(request.page, request.count)