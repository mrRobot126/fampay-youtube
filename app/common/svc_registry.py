import logging
from pipeline.common.svc import AsycnS3Service, DatabaseConnectionSvc, ServiceKey, AsyncVespaService, AsyncIndexingSvc, TelegramAsyncIndexerDBService
from pipeline.common.svc.db_conn_pool_svc import DatabaseConnectionPoolSvc

class SvcRegistry:

    logger = logging.getLogger(__name__)
    svc_dict = {}

    def __init__(self, config) -> None:
        self.config = config

    async def initialise(self):
        s3_key, s3_session = await self._initialise_s3_session()
        self.svc_dict[s3_key] = s3_session

        db_conn_key, db_conn = await self._initialise_db_pool_client()
        self.svc_dict[db_conn_key] = db_conn

        indexer_db_key, indexer_db_svc = await self._initialise_indexer_db_svc(db_conn)
        self.svc_dict[indexer_db_key] = indexer_db_svc

        vespa_key, vespa = await self._initialise_vespa_client()
        self.svc_dict[vespa_key] = vespa

        indexing_svc_key, indexing_svc = await self._initialise_indexing_svc(indexer_db_svc, vespa)
        self.svc_dict[indexing_svc_key] = indexing_svc

    @classmethod
    def get_svc(cls, key: ServiceKey):
        if cls.svc_dict[key]:
            return cls.svc_dict[key].get()
        else:
            raise ValueError("Service not registred for key: {}".format(key))

    async def _initialise_db_client(self):
        CONN_STRING = self.config["db_conn"]
        conn = DatabaseConnectionSvc(CONN_STRING)
        await conn.init()
        return (ServiceKey.DB_CONN, conn)

    async def _initialise_db_pool_client(self):
        CONN_STRING = self.config["db_conn"]
        conn = DatabaseConnectionPoolSvc(CONN_STRING)
        await conn.init()
        return (ServiceKey.DB_CONN, conn)

    async def _initialise_indexer_db_svc(self, conn):
        indexer_db_svc = TelegramAsyncIndexerDBService(conn)
        await indexer_db_svc.init()
        return (ServiceKey.INDEXER_DB_SVC, indexer_db_svc)

    async def _initialise_s3_session(self):
        AWS_ACCESS_KEY = self.config["aws_access_key_id"]
        AWS_ACCESS_SECRET = self.config["aws_access_key_secret"]
        s3_session = AsycnS3Service(AWS_ACCESS_KEY, AWS_ACCESS_SECRET)
        await s3_session.init()
        return (ServiceKey.S3_SESSION, s3_session)
    
    async def _initialise_vespa_client(self):
        VESPA_URL = self.config["vespa_url"]
        vespa_svc = AsyncVespaService(VESPA_URL)
        await vespa_svc.init()
        return (ServiceKey.VESPA, vespa_svc)

    async def _initialise_indexing_svc(self, index_db_svc: TelegramAsyncIndexerDBService, vespa_svc: AsyncVespaService):
        indexing_svc = AsyncIndexingSvc()
        await indexing_svc.init(index_db_svc, vespa_svc)
        return (ServiceKey.INDEXING_SVC, indexing_svc)

    async def terminate(self):
        self.logger.info("Terminating Svc..")
        for svc in self.svc_dict:
            await self.svc_dict[svc].terminate()
        self.logger.info("Done Terminating Svc..")
