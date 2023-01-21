import logging
from core.indexer import VideoIndexerOrchestrator
from common.svc.base_svc import ServiceKey
from common.svc.db_conn_svc import DatabaseConnectionPoolSvc
from common.svc.impl.postgres.pg_config_db_svc import PostgresConfigDBService
from common.svc.impl.postgres.pg_vc_db_svc import PostgresVideoCatalogDBService
from common.svc.impl.postgres.pg_vc_search_svc import PostgresVCSearchService
from common.svc.video_vendor_svc import VideoVendorService
from common.constants import VideoVendor, AuthMethod

class SvcRegistry:

    logger = logging.getLogger(__name__)
    svc_dict = {}

    def __init__(self, config) -> None:
        self.config = config

    async def initialise(self):
        db_conn_key, db_conn = await self._initialise_db_pool_client()
        self.svc_dict[db_conn_key] = db_conn

        config_svc_key, config_svc = await self._initialise_pg_config_svc(db_conn)
        self.svc_dict[config_svc_key] = config_svc

        vc_db_svc_key, vc_db_svc = await self._initialise_pg_vc_db_svc(db_conn)
        self.svc_dict[vc_db_svc_key] = vc_db_svc

        vc_search_svc_key, vc_search_svc = await self._initialise_pg_search_svc(db_conn)
        self.svc_dict[vc_search_svc_key] = vc_search_svc

        video_vendor_svc_key, video_vendor_svc = await self._initialise_video_vendor_svc(config_svc)
        self.svc_dict[video_vendor_svc_key] = video_vendor_svc

        video_indexer_key, video_indexer = await self._initialise_video_indexer(config_svc, video_vendor_svc, vc_db_svc, self.config['query'])
        self.svc_dict[video_indexer_key] = video_indexer

    @classmethod
    def get_svc(cls, key: ServiceKey):
        if cls.svc_dict[key]:
            return cls.svc_dict[key].get()
        else:
            raise ValueError("Service not registred for key: {}".format(key))

    async def _initialise_db_pool_client(self):
        CONN_STRING = self.config["db_conn"]
        conn = DatabaseConnectionPoolSvc(CONN_STRING)
        await conn.init()
        return (ServiceKey.DB_CONN, conn)

    async def _initialise_pg_vc_db_svc(self, conn):
        vc_db_svc = PostgresVideoCatalogDBService(conn)
        await vc_db_svc.init()
        return (ServiceKey.VC_DB_SVC, vc_db_svc)
    
    async def _initialise_pg_config_svc(self, conn):
        vc_config_svc = PostgresConfigDBService(conn)
        await vc_config_svc.init()
        return (ServiceKey.CONFIG_SVC, vc_config_svc)
    
    async def _initialise_pg_search_svc(self, conn):
        vc_search_svc = PostgresVCSearchService(conn)
        await vc_search_svc.init()
        return (ServiceKey.VC_SEARCH_SVC, vc_search_svc)

    async def _initialise_video_vendor_svc(self, config_db_svc):
        video_vendor_svc = VideoVendorService(config_db_svc, VideoVendor.GOOGLE, AuthMethod.AUTH_TOKEN)
        await video_vendor_svc.init()
        return (ServiceKey.VIDEO_VENDOR_SVC, video_vendor_svc)

    async def _initialise_video_indexer(self, config_svc, video_vendor, catalog_svc, query):
        video_indexer_svc = VideoIndexerOrchestrator(config_svc, video_vendor, catalog_svc, search_query=query)
        return (ServiceKey.VIDEO_INDEXER_SVC, video_indexer_svc)