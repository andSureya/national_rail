# in-built
import traceback

# custom
from network_rail.config.app_config import logger, module_root_directory
from network_rail.config.env_config import USERNAME, PASSWORD
from network_rail.feeds.authorize import Authorize
from network_rail.schemas.feed_config import FeedConfig
from network_rail.repositories.feed_repository import Feed


class NationalRailSnapshot:

    def __init__(
            self, fares: Feed, movement: Feed,
            routing: Feed
    ):
        try:
            self.username = USERNAME
            self.password = PASSWORD

            self.fares = fares
            self.movement = movement
            self.routing = routing

            self.authorize = Authorize(
                username=self.username, password=self.password
            )

        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())
            raise Exception("Error fetching token")

    def extract(self):
        self.authorize.get_token()

        config: FeedConfig = FeedConfig(
            storage_path=module_root_directory, auth=self.authorize
        )

        self.fares.fetch(config=config)
        self.routing.fetch(config=config)
        self.movement.fetch(config=config)

        logger.info("Completed extraction")
