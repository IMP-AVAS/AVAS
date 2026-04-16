import logging
from logger.logger_config import setup_logger
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    setup_logger(
        level=logging.INFO,
    )

    logger.info('hello world')