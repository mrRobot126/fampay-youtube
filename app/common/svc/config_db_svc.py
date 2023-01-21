from abc import ABC, abstractmethod
from collections import namedtuple
from typing import List
from common.constants import AuthStatus, VideoVendor, AuthMethod
from datetime import datetime

last_sync_tuple = namedtuple('LastSyncTime', 'vendor last_sync_time')
auth_record = namedtuple('AuthRecord', 'id vendor method status config')

class ConfigDBService(ABC):

    @abstractmethod
    def get_last_sync_time_for_vendor(self, vendor: VideoVendor) -> last_sync_tuple:
        pass

    @abstractmethod
    def upsert_last_sync_time_for_vendor(self, vendor: VideoVendor, time: datetime):
        pass

    @abstractmethod
    def insert_auth_token(self, vendor: VideoVendor, auth_method: AuthMethod, config):
        pass

    @abstractmethod
    def update_auth_status(self, auth_id: int, status: AuthStatus):
        pass

    @abstractmethod
    def get_record_for_vendor_and_method_and_status(self, vendor: VideoVendor, method: AuthMethod, status: AuthStatus) -> List[auth_record]:
        pass