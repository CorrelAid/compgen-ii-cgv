import logging
from datetime import datetime

from .gov_extraction import GOV
from .gov_matching import Matcher
from .pipeline import Pipeline


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_logger = logging.FileHandler(f"{datetime.now():%Y-%m-%d-%H-%M-%S}_compgen2.log")
file_logger.setLevel(logging.DEBUG)
fileformat = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(lineno)04d | %(message)s", datefmt="%H:%M:%S"
)
file_logger.setFormatter(fileformat)

logger.addHandler(file_logger)

stream_logger = logging.StreamHandler()
stream_logger.setLevel(logging.INFO)
streamformat = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s")
stream_logger.setFormatter(streamformat)


logger.addHandler(stream_logger)
