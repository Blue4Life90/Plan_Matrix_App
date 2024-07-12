import os
import logging
from constants import TRACKING_LOGS_DIR

def setup_logging(entry_log_file=None):
    if not os.path.exists(TRACKING_LOGS_DIR):
        os.makedirs(TRACKING_LOGS_DIR)

    # Logger for entry modifications
    entry_logger = logging.getLogger('entry_logger')
    for handler in entry_logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            handler.close()
        entry_logger.removeHandler(handler)
    
    entry_logger.setLevel(logging.INFO)
    entry_logger.propagate = False  # Prevent log propagation
    if entry_log_file:
        entry_handler = logging.FileHandler(entry_log_file)
        entry_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        entry_logger.addHandler(entry_handler)

    # Logger for application errors
    error_logger = logging.getLogger('error_logger')
    for handler in error_logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            handler.close()
        error_logger.removeHandler(handler)
    
    error_logger.setLevel(logging.ERROR)
    error_logger.propagate = False  # Prevent log propagation
    error_log_file = os.path.join(TRACKING_LOGS_DIR, 'app.log')
    error_handler = logging.FileHandler(error_log_file)
    error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    error_logger.addHandler(error_handler)

    return entry_logger, error_logger

