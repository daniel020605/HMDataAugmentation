import logging
import os

log_directory = './logs'
os.makedirs(log_directory, exist_ok=True)

def setup_logger(name, log_file, level=logging.INFO):
    """Function to setup a logger; can be used to create multiple loggers"""
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    logger.addHandler(console_handler)

    return logger

# Example usage
if __name__ == "__main__":
    logger = setup_logger('example_logger', os.path.join(log_directory, 'example.log'))
    logger.info('This is an info message')
    logger.error('This is an error message')