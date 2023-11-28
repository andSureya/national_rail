from dataclasses import dataclass

# custom
from network_rail.feeds.authorize import Authorize


@dataclass
class FeedConfig:
    storage_path: str
    auth: Authorize
