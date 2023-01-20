import json
import logging
from typing import List
from app.common.svc.base_svc import BaseAsyncService
from app.common.svc.config_db_svc import ConfigDBService, last_sync_tuple, auth_record
from app.common.svc.db_conn_svc import DatabaseConnectionPoolSvc
from app.common.constants import AuthStatus


class PostgresConfigDBService(BaseAsyncService, ConfigDBService):

    logger = logging.getLogger(__name__)

    def __init__(self, conn_svc) -> None:
        self.conn_svc: DatabaseConnectionPoolSvc = conn_svc

    async def init(self):
        self.conn: DatabaseConnectionPoolSvc = self.conn_svc.get()

    async def terminate(self):
        pass

    def get(self):
        return self
        
    async def get_last_sync_time_for_vendor(self, vendor: str) -> last_sync_tuple:
        record = await self.conn_svc.fetchrow(
            """
                SELECT
                *
                FROM config c
                WHERE c.vendor == $1
            """,
            vendor
        )

        if (record == None):
            return None
        else:
            return last_sync_tuple(record['vendor'], record['last_sync_time'])


    async def get_record_for_vendor_and_method_and_status(self, vendor: str, method: str, status: AuthStatus) -> List[auth_record]:
        records = await self.conn_svc.fetch(
            """
                SELECT
                *
                FROM auth_tokens at
                WHERE at.vendor = $1 AND at.method = $2 AND at.status = $3
            """,
            vendor,
            method,
            status
        )

        if records:
            return [
                self._parse_auth_record(r) for r in records
            ]
        else:
            return []
    
    async def update_auth_status(self, auth_id: int, status: AuthStatus):
         await self.conn.execute(
            """
                UPDATE auth_tokens SET status = $1 WHERE auth_id = $2
            """,
            status,
            auth_id
        )

    def _parse_auth_record(self, record) -> auth_record:
        return auth_record(record['id'], record['vendor'], record['method'], json.loads(record['config']))