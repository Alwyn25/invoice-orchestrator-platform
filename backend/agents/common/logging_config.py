import logging
import os
import sys

def configure_logging(service_name: str):
    """
    Configures standardized logging for agent services.

    Args:
        service_name: The name of the service to include in log messages.
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Get the root logger
    logger = logging.getLogger()

    # Remove any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(log_level)

    # Create a handler to write to stdout
    handler = logging.StreamHandler(sys.stdout)

    # Create a formatter and add it to the handler
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(service_name)s] - %(message)s'
    )
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    # Add service_name to the log record using a filter
    class ServiceNameFilter(logging.Filter):
        def filter(self, record):
            record.service_name = service_name
            return True

    logger.addFilter(ServiceNameFilter())
