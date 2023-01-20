from core.video_catalog_svc import get_paginated_catalog, search_video
from common.models import VideoCatalogSearchResponse, VideoCatalogResponse, VideoCatalogRequest, VideoSearchRequest
from common.svc_registry import SvcRegistry
from core.indexer import VideoIndexer
from fastapi import FastAPI
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


@app.on_event("startup")
async def startup():
    svc_registry = SvcRegistry(
        {
            "db_conn": "postgresql://postgres:secret@127.0.0.1:6000/fampay"
        }
    )
    await svc_registry.initialise()
    indexer = VideoIndexer()
    await indexer.fetch_videos()


@app.post("/search", response_model=VideoCatalogSearchResponse)
async def get_search_response(request: VideoSearchRequest):
    return await search_video(request=request)

@app.post("/list", response_model=VideoCatalogResponse)
async def list_videos(request: VideoCatalogRequest):
    return await get_paginated_catalog(request.page, request.count)