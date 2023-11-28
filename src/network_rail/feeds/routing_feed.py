# in-built
import io
import re
import traceback
import zipfile
from os.path import join, splitext
from typing import List, Tuple

# 3rd party
import requests
import pandas as pd
from tqdm import tqdm

# custom
from network_rail.repositories.feed_repository import Feed
from network_rail.schemas.feed_config import FeedConfig
from network_rail.config.app_config import logger


class RoutingFeed(Feed):
    def __init__(self):
        self.url = "https://opendata.nationalrail.co.uk/api/staticfeeds/2.0/routeing"
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
            logger.info("Routing feed completed")

        else:
            logger.error(response)
            logger.error(traceback.format_exc())
            logger.error("Error downloading fares feed")

    @staticmethod
    def parse_permitted_routes_line_item(line: str) -> List[Tuple[str, str, str]]:
        if line[0].isalpha():
            records: List[Tuple[str, str, str]] = []
            nodes = line.split(",")
            for node in nodes[2:]:
                node_from = nodes[0]
                node_to = nodes[1]
                records.append(
                    (node_from, node_to, node)
                )
            return records

    def parse_permitted_routes_file(self, filename, zip_ref) -> pd.DataFrame:
        file_content = zip_ref.read(filename)
        lines = file_content.splitlines()

        _clean_records = []

        for line in tqdm(lines, desc="Processing Permitted route records"):
            _records = self.parse_permitted_routes_line_item(
                line=line.decode('utf-8')
            )

            if _records:
                _clean_records.extend(_records)

        df = pd.DataFrame(data=_clean_records, columns=['from', 'to', 'via'])
        return df

    @staticmethod
    def parse_permitted_node_file(filename, zip_ref) -> pd.DataFrame:
        _records = []
        file_content = zip_ref.read(filename)
        lines = file_content.splitlines()

        data_lines = [
            line.strip().decode("utf-8")
            for line in lines
            if not line.decode("utf-8").startswith('/!!')
        ]

        for i in tqdm(range(0, len(data_lines), 2), desc="Processing Node lines"):
            code = data_lines[i + 1]
            name = data_lines[i]
            clean_name = re.sub(r'[^a-zA-Z\s]', '', name)
            _records.append(
                (code, clean_name)
            )

        df = pd.DataFrame(data=_records, columns=['node', 'name'])
        return df

    def persist_response_content(self, response: requests.Response, config: FeedConfig) -> pd.DataFrame:
        zip_content = io.BytesIO(response.content)

        with (zipfile.ZipFile(zip_content, 'r') as zip_ref):
            file_list = zip_ref.namelist()
            permitted_routes = [
                x
                for x in file_list
                if x.endswith('.RGR')
            ]

            nodes = [
                x
                for x in file_list
                if x.endswith('.RGN')
            ]

            routes_dfs = []
            node_dfs = []
            for file_name in permitted_routes:
                _df = self.parse_permitted_routes_file(filename=file_name, zip_ref=zip_ref)
                if _df is not None:
                    routes_dfs.append(_df)

            for file_name in nodes:
                _df = self.parse_permitted_node_file(filename=file_name, zip_ref=zip_ref)
                if _df is not None:
                    node_dfs.append(_df)

            routes = pd.concat(routes_dfs, ignore_index=True).reset_index()
            nodes = pd.concat(node_dfs, ignore_index=True).reset_index()

            routes.to_csv(
                join(config.storage_path, "routing_permitted_routes.csv"), index=False
            )

            nodes.to_csv(
                join(config.storage_path, "routing_nodes.csv"), index=False
            )
