import datetime
import json
import logging
from typing import List
from common.svc.base_svc import BaseAsyncService
from common.svc.config_db_svc import ConfigDBService, last_sync_tuple, auth_record
from common.svc.db_conn_svc import DatabaseConnectionPoolSvc
from common.constants import AuthStatus, VideoVendor, AuthMethod

"""
Postgresql Implementation of ConfigDBService
"""
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

    async def insert_auth_token(self, vendor: VideoVendor, auth_method: AuthMethod, config):
        await self.conn_svc.execute(
            """
                INSERT INTO auth_tokens(vendor, auth_method, config) VALUES($1, $2, $3)
            """,
            vendor.value,
            auth_method.value,
            json.dumps(config)
        )
        
    async def get_last_sync_time_for_vendor(self, vendor: VideoVendor) -> last_sync_tuple:
        record = await self.conn_svc.fetchrow(
            """
                SELECT
                    c.vendor,
                    c.last_sync_time
                FROM config c
                WHERE c.vendor = $1
            """,
            vendor.value
        )

        if (record == None):
            return None
        else:
            return last_sync_tuple(record['vendor'], record['last_sync_time'])


    async def upsert_last_sync_time_for_vendor(self, vendor: VideoVendor, time: datetime):
        await self.conn.execute(
            """
                INSERT INTO config(vendor, last_sync_time) VALUES($1, $2)
                ON CONFLICT(vendor)
                DO UPDATE SET 
                last_sync_time = excluded.last_sync_time
            """,
            vendor.value,
            time
        )

    async def get_record_for_vendor_and_method_and_status(self, vendor: VideoVendor, method: AuthMethod, status: AuthStatus) -> List[auth_record]:
        self.logger.error('%s %s %s', vendor, method, status.value)
        records = await self.conn_svc.fetch(
            """
                SELECT
                at.id,
                at.vendor,
                at.method,
                at.config,
                at.status
                FROM auth_tokens at
                WHERE at.vendor = $1 AND at.method = $2 AND at.status = $3
            """,
            vendor.value,
            method.value,
            status.value
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
                UPDATE auth_tokens SET status = $1 WHERE id = $2
            """,
            status.value,
            auth_id
        )

    def _parse_auth_record(self, record) -> auth_record:
        return auth_record(record['id'], record['vendor'], record['method'], record['status'], json.loads(record['config']))