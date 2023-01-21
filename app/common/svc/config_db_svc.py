from abc import ABC, abstractmethod
from collections import namedtuple
from typing import List
from common.constants import AuthStatus, VideoVendor, AuthMethod
from datetime import datetime

last_sync_tuple = namedtuple('LastSyncTime', 'vendor last_sync_time')
auth_record = namedtuple('AuthRecord', 'id vendor method status config')

"""
Skeleton of ConfigDBService
"""
class ConfigDBService(ABC):

    """
    Fetches last sync time for different video vendors. Helps to always fetch videos published after previous sync
    """
    @abstractmethod
    def get_last_sync_time_for_vendor(self, vendor: VideoVendor) -> last_sync_tuple:
        pass

    """
    Update last sync time for different Vendors
    """
    @abstractmethod
    def upsert_last_sync_time_for_vendor(self, vendor: VideoVendor, time: datetime):
        pass

    """
    Insert Different Auth Records for respective Vendors
    Also provides AuthMethod to support different auth processes
    """
    @abstractmethod
    def insert_auth_token(self, vendor: VideoVendor, auth_method: AuthMethod, config):
        pass

    """
    Update Auth Status of Vendors
    """
    @abstractmethod
    def update_auth_status(self, auth_id: int, status: AuthStatus):
        pass

    """
    Fetch Auth Record for a particular vendor, method and status
    """
    @abstractmethod
    def get_record_for_vendor_and_method_and_status(self, vendor: VideoVendor, method: AuthMethod, status: AuthStatus) -> List[auth_record]:
        pass