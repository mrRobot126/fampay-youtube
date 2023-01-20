from abc import ABC, abstractmethod
from collections import namedtuple
from typing import List
from app.common.constants import AuthStatus

last_sync_tuple = namedtuple('LastSyncTime', 'id vendor last_sync_time')
auth_record = namedtuple('AuthRecord', 'id vendor method status config')

class ConfigDBService(ABC):

    @abstractmethod
    def get_last_sync_time_for_vendor(self, vendor: str) -> last_sync_tuple:
        pass

    @abstractmethod
    def insert_auth_token(self, vendor: str, auth_method: str, config):
        pass

    @abstractmethod
    def update_auth_status(self, auth_id: int, status: AuthStatus):
        pass

    @abstractmethod
    def get_record_for_vendor_and_method_and_status(self, vendor: str, method: str, status: AuthStatus) -> List[auth_record]:
        pass