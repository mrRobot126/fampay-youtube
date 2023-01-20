
import enum


class SortOrder(enum.Enum):
    DESC = "desc"
    ASC = "asc"

class QueryType(enum.Enum):
    PHRASE = "phrase"

class AuthStatus(enum.Enum):
    ACTIVE = 'active'
    REVOKED = 'revoked'
    QUOTA_EXCEEDED = 'quota_exceeded'