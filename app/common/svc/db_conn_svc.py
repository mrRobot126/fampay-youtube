import logging
from common.svc.base_svc import BaseAsyncService
import asyncpg

"""
Connection Pool Implementation for DB
This Helps us to better control DB connections especially in async environments
TODO: Make min_size and max_size configurable though env variables
"""
class DatabaseConnectionPoolSvc(BaseAsyncService):
    def __init__(self, conn_string):
        self.connection_pool = None
        self.conn_string = conn_string
        self.logger = logging.getLogger(__name__)

    async def init(self):
        self.connection_pool = await asyncpg.create_pool(dsn = self.conn_string, min_size=10, max_size=20)
        return self.connection_pool

    async def terminate(self):
        # its executed when connection close
        await self.connection_pool.close()

    def get(self):
        return self

    async def fetch(self, query, *args):
        con = await self.connection_pool.acquire()
        try:
            result = await con.fetch(query, *args)
            return result
        except Exception as e:
                self.logger.exception(e)
        finally:
            await self.connection_pool.release(con)

    async def fetchrow(self, query, *args):
        con = await self.connection_pool.acquire()
        try:
            result = await con.fetchrow(query, *args)
            return result
        except Exception as e:
                self.logger.exception(e)
        finally:
            await self.connection_pool.release(con)
    
    async def execute(self, query, *args):
        con = await self.connection_pool.acquire()
        try:
            result = await con.execute(query, *args)
            return result
        except Exception as e:
                self.logger.exception(e)
        finally:
            await self.connection_pool.release(con)
