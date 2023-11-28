# in-built
import io
import sys
import gzip
import time
import socket
import logging
import traceback
from os.path import join

# 3rd party
import stomp
import xmltodict
import pandas as pd
from tqdm import tqdm

# custom
from network_rail.config.app_config import logger
from network_rail.schemas.feed_config import FeedConfig
from network_rail.repositories.feed_repository import Feed


class StompClient(stomp.ConnectionListener):
    def __init__(self, config: FeedConfig):
        self.record_count = 0
        self.file_counter = 1
        self.records_per_file = 10000
        self.config = config
        self.file_path = join(self.config.storage_path, "movement.csv")
        self.raw_dataset = []

    def on_heartbeat(self):
        logging.info('Received a heartbeat')

    def on_heartbeat_timeout(self):
        logging.error('Heartbeat timeout')

    def on_error(self, headers, message):
        logging.error(message)

    def on_disconnected(self):
        _delay: int = 1
        time.sleep(_delay)
        sys.exit(0)

    @staticmethod
    def exit_gracefully():
        _delay: int = 1
        logging.warning('Exiting gracefully - waiting %s seconds before exiting' % _delay)
        time.sleep(_delay)
        sys.exit(0)

    def on_connecting(self, host_and_port):
        logging.info('Connecting to ' + host_and_port[0])

    def on_message(self, frame):
        try:
            bio = io.BytesIO()
            bio.write(str.encode('utf-16'))
            bio.seek(0)
            decompressed_data = gzip.decompress(frame.body)
            xml_dict = xmltodict.parse(decompressed_data)
            self.raw_dataset.append(xml_dict)

            self.record_count += 1

            # Check if record count reaches the limit
            if self.record_count >= self.records_per_file:
                data_frames = [
                    pd.json_normalize(item)
                    for item in tqdm(self.raw_dataset, desc="Processing downloaded feed")

                ]
                result = pd.concat(data_frames, ignore_index=True).reset_index()
                result.to_csv(self.file_path, index=False)
                self.exit_gracefully()

        except Exception as e:
            logging.error(str(e))
            print(traceback.format_exc())


class MovementFeed(Feed):
    def __init__(self):
        self.username = 'DARWIN3b086483-66d7-4abc-87d8-6fd1b7334faa'
        self.password = 'c11a911f-7f11-45a6-9ce8-6147d24e6bde'
        self.hostname = 'darwin-dist-44ae45.nationalrail.co.uk'
        self.hostport = 61613
        self.topic = '/topic/darwin.pushport-v16'
        self.client_id = socket.getfqdn()
        self.heartbeat_interval_ms = 15000

        self.connection = stomp.Connection12(
            [(self.hostname, self.hostport)],
            auto_decode=False,
            heartbeats=(self.heartbeat_interval_ms, self.heartbeat_interval_ms)
        )

    def connect_and_subscribe(self):
        logger.info("Extracting realtime feed")

        connect_header = {
            'client-id': self.username + '-' + self.client_id
        }

        subscribe_header = {
            'activemq.subscriptionName': self.client_id
        }

        self.connection.connect(
            username=self.username,
            passcode=self.password,
            wait=True,
            headers=connect_header
        )

        self.connection.subscribe(
            destination=self.topic,
            id='1',
            ack='auto',
            headers=subscribe_header
        )

    def fetch(self, config: FeedConfig):
        stomp_client = StompClient(config=config)
        self.connection.set_listener('', stomp_client)
        self.connect_and_subscribe()

        while stomp_client.record_count < stomp_client.records_per_file:
            time.sleep(1)

        stomp_client.exit_gracefully()
        logger.info("Completed")
