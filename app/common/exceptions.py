## This file will contain all exceptions

class APIQuotaExpiredException(Exception):
    def __init__(self, message: str = "API Limit Exceeded") -> None:
        self.message = message
        super().__init__(self.message)

class IndexerWentBonkers(Exception):
    def __init__(self, message: str = "Indexer Went Bonkers!!") -> None:
        self.message = message
        super().__init__(self.message)


class APIClientWentBonkers(Exception):
    def __init__(self,  vendor: str, message: str = "Indexer Went Bonkers!!") -> None:
        self.message = message
        self.vendor = vendor
        super().__init__(self.message)