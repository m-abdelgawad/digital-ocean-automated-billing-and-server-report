import os
import sys
import inspect
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_app_logger(logger_name, log_file_path=None):

    # Create a logger
    logger = logging.getLogger(logger_name)

    # Set the level of logging
    logger.setLevel(logging.DEBUG)

    # Set the format of the log message
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Set the log handler
    log_handler = logging.StreamHandler(sys.stdout)

    # Set the log message format we've created to the log handler
    log_handler.setFormatter(formatter)

    # Clear any previous handlers and add a new handler
    logger.handlers.clear()
    logger.addHandler(log_handler)

    # Check if the function received a file name; to insert the logs inside it
    if log_file_path:

        # Set a FileHandler write the logs inside the file
        file_handler = RotatingFileHandler(
            filename=log_file_path, mode='a', maxBytes=5*1024*1024,
            backupCount=100, encoding='utf8', delay=False
        )

        # Set the format of the FileHandler
        file_handler.setFormatter(formatter)

        # Add the filehandler
        logger.addHandler(file_handler)

    # Return the logger
    return logger


def create_log_file(app_name, parent_dir_path):

    # Create logs folder if not exists
    logs_folder_path = os.path.join(parent_dir_path, 'logs')
    if not os.path.exists(logs_folder_path):
        os.makedirs(logs_folder_path)

    # Get current timestamp
    current_timestamp = str(datetime.now().strftime("%Y-%m-%d__%H-%M-%S"))

    # Logs file name
    logs_file_name = app_name + "__" + current_timestamp + ".log"

    # Logs file path
    logs_file_path = os.path.join(parent_dir_path, 'logs', logs_file_name)

    # Create the logs file if not exists
    if not os.path.exists(logs_file_path):
        open(logs_file_path, 'w').close()

    return logs_file_path


def get(app_name='logs', enable_logs_file=True):

    if enable_logs_file:

        # Get absolute path of the caller module
        caller_abs_path = inspect.stack()[1].filename

        # Get the absolute path of the Repo directory
        # which is the parent directory of the parent directory of __main__.py
        # that supposes to call this function
        repo_abs_path = os.path.dirname(os.path.dirname(caller_abs_path))

        # Create the logs file
        logs_file_path = create_log_file(
            app_name=app_name, parent_dir_path=repo_abs_path
        )

        # Create the logger
        logger = setup_app_logger(logger_name='', log_file_path=logs_file_path)

    else:

        # Create the logger
        logger = setup_app_logger(logger_name='', log_file_path=None)

    # Return the logger
    return logger
