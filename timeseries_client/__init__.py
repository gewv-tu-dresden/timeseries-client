from timeseries_client.timeseries_client import TimeseriesClient
from loguru import logger

# disable logger on default because this is a lib
logger.disable(__name__)

__version__ = "0.2.0"
__all__ = ["TimeseriesClient"]
