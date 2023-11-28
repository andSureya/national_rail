import logging
import traceback
from os.path import abspath, join, exists
from os import getcwd, makedirs

try:
    application_name = "national-rail-data-feed-extractor"
    module_root_directory = join(abspath(getcwd()), "outputs")

    if not exists(module_root_directory):
        makedirs(module_root_directory)

    log_level = logging.INFO
    logger = logging.getLogger(application_name)
    logger.setLevel(log_level)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    formatter = logging.Formatter('[%(filename)s:%(lineno)d] - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
except Exception as e:
    print("Error initialising app")
    print(e)
    print(traceback.format_exc())
