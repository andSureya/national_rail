# in-built
import warnings
from argparse import ArgumentParser

# custom
from network_rail.config.app_config import module_root_directory
from network_rail.extractor.snapshot import NationalRailSnapshot
from network_rail.feeds.fares_feed import FaresFeed
from network_rail.feeds.movement_feed import MovementFeed
from network_rail.feeds.routing_feed import RoutingFeed


warnings.filterwarnings('ignore')


def main():
    snapshot_extraction: NationalRailSnapshot = NationalRailSnapshot(
        routing=RoutingFeed(),
        fares=FaresFeed(),
        movement=MovementFeed()
    )

    snapshot_extraction.extract()


if __name__ == '__main__':
    main()
