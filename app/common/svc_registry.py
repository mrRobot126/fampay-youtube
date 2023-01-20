import logging
from app.common.svc.base_svc import ServiceKey
from app.common.svc.db_conn_svc import DatabaseConnectionPoolSvc
from app.common.svc.impl.postgres.pg_config_db_svc import PostgresConfigDBService
from app.common.svc.impl.postgres.pg_vc_db_svc import PostgresVideoCatalogDBService

class SvcRegistry:

    logger = logging.getLogger(__name__)
    svc_dict = {}

    def __init__(self, config) -> None:
        self.config = config

    async def initialise(self):
        pass

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
        return (ServiceKey.VC_DB_SVC, vc_db_svc)
    
    async def _initialise_pg_config_svc(self, conn):
        vc_config_svc = PostgresConfigDBService(conn)
        return (ServiceKey.CONFIG_SVC, vc_config_svc)
    
    async def _initialise_pg_search_svc(self, conn):
        vc_search_svc = PostgresConfigDBService(conn)
        return (ServiceKey.VC_SEARCH_SVC, vc_search_svc)