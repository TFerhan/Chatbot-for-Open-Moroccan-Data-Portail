import logging
import os



def setup_logging(log_file='app.log'):

    # Create a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  # Set the logging level

    # Create a formatter that includes the date and time
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Create file handler, appending to the log file
    file_handler = logging.FileHandler(log_file, mode='a')  # 'a' for append mode
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Ensure the log file is in the same directory as the script
    if not os.path.exists(log_file):
        with open(log_file, 'w'):  # Create the file if it doesn't exist
            pass

    return logger

# Create a logger instance using the setup_logging function
logger = setup_logging()

# Ignore warnings in the terminal
