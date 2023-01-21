
import enum


class SortOrder(enum.Enum):
    DESC = "desc"
    ASC = "asc"

class QueryType(enum.Enum):
    PHRASE = "phrase"
    DEFAULT = "default"

class AuthStatus(enum.Enum):
    ACTIVE = 'active'
    ELIGIBLE = 'eligible'
    REVOKED = 'revoked'
    QUOTA_EXCEEDED = 'quota_exceeded'

class IndexerCancelReason(enum.Enum):
    QUOTA_EXPIRY = 'quota_expiry'
    API_CLIENT = 'api_client'
    UNKNOWN = 'unknown'

class VideoVendor(enum.Enum):
    GOOGLE = 'google'

class AuthMethod(enum.Enum):
    AUTH_TOKEN = 'auth_token'

class VideoSource(enum.Enum):
    YOUTUBE = 'youtube'

PAGE_SIZE = 5