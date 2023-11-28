# in-built
import io
import traceback
import zipfile
from os.path import join, splitext

# 3rd party
import requests
import pandas as pd
from tqdm import tqdm

# custom
from network_rail.config.app_config import logger
from network_rail.schemas.feed_config import FeedConfig
from network_rail.repositories.feed_repository import Feed


class FaresFeed(Feed):

    def __init__(self):
        self.url = "https://opendata.nationalrail.co.uk/api/staticfeeds/2.0/fares"
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Host': 'opendata.nationalrail.co.uk'
        }

    def fetch(self, config: FeedConfig):
        self.headers.update({'X-Auth-Token': config.auth.token})
        response = requests.get(
            url=self.url, headers=self.headers, verify=False
        )
        if response.status_code == 200:
            self.persist_response_content(response=response, config=config)
        else:
            logger.error(response)
            logger.error(traceback.format_exc())
            logger.error("Error downloading fares feed")

    @staticmethod
    def parse_record(record):
        parsed_fields = {
            "UPDATE_MARKER": record[0:1] if len(record) >= 1 else None,
            "RECORD_TYPE": record[1:2] if len(record) >= 2 else None,
            "ORIGIN_CODE": record[2:6] if len(record) >= 6 else None,
            "DESTINATION_CODE": record[6:10] if len(record) >= 10 else None,
            "ROUTE_CODE": record[10:15] if len(record) >= 15 else None,
            "STATUS_CODE": record[15:18] if len(record) >= 18 else None,
            "USAGE_CODE": record[18:19] if len(record) >= 19 else None,
            "DIRECTION": record[19:20] if len(record) >= 20 else None,
            "END_DATE": record[20:28] if len(record) >= 28 else None,
            "START_DATE": record[28:36] if len(record) >= 36 else None,
            "TOC": record[36:39] if len(record) >= 39 else None,
            "CROSS_LONDON_IND": record[39:40] if len(record) >= 40 else None,
            "NS_DISC_IND": record[40:41] if len(record) >= 41 else None,
            "PUBLICATION_IND": record[41:42] if len(record) >= 42 else None,
            "FLOW_ID": record[42:49] if len(record) >= 49 else None,
        }
        return parsed_fields

    def parse_fare_line_item(self, line: str):
        if line.startswith("/!!"):
            return
        else:
            return self.parse_record(record=line)

    def persist_response_content(self, response: requests.Response, config: FeedConfig) -> None:
        zip_content = io.BytesIO(response.content)

        with zipfile.ZipFile(zip_content, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            fare_files = [x for x in file_list if x.endswith('.FFL')]

            for file_name in fare_files:
                base,ext = splitext(file_name)
                file_content = zip_ref.read(file_name)
                lines = file_content.splitlines()
                records = [
                    self.parse_fare_line_item(line=line.decode('utf-8'))
                    for line in tqdm(lines, desc="Processing fare records")
                ]

                filtered_list = list(filter(lambda x: x is not None, records))
                df = pd.DataFrame(data=filtered_list)
                df.to_csv(join(config.storage_path, f"fares_{base}.csv"), index=False)
