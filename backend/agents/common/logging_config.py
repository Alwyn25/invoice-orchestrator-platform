import logging
import os
import sys

def configure_logging(service_name: str, correlation_id: str = "NO_CORRELATION_ID"):
    """
    Configures standardized logging for agent services.

    Args:
        service_name: The name of the service to include in log messages.
        correlation_id: A unique identifier for a request or flow.
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    logger = logging.getLogger()

    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(log_level)

    handler = logging.StreamHandler(sys.stdout)

    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(service_name)s] [%(correlation_id)s] - %(message)s'
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    class ContextFilter(logging.Filter):
        def filter(self, record):
            record.service_name = service_name
            record.correlation_id = correlation_id
            return True

    logger.addFilter(ContextFilter())
