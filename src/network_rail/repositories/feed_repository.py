# in-built
from abc import ABC, abstractmethod

# custom
from network_rail.schemas.feed_config import FeedConfig


class Feed(ABC):

    @abstractmethod
    def fetch(self, config: FeedConfig):
        pass
