# 3rd party
import traceback

import requests

# custom
from network_rail.config.app_config import logger


class Authorize:
    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.url = "https://opendata.nationalrail.co.uk/authenticate"
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        self.payload = {
            'username': username,
            'password': password
        }

        self.token = None
        self.metadata = None

    def get_token(self):
        try:
            response = requests.post(
                url=self.url, headers=self.headers, data=self.payload, verify=False
            )

            self.metadata = response.json()
            self.token = self.metadata['token']
        except Exception as e:
            logger.error(e)
            logger.error(traceback.format_exc())
            raise Exception("Error Authenticating user credentials")

