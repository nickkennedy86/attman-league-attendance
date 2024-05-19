import logging.handlers
import logging
import sys

def setup_logger(level):
    logger = logging.getLogger('attman_logger')
    logger.setLevel(level)
    log_format = logging.Formatter(fmt='%(asctime)s - %(filename)s - %(levelname)s - %(message)s',datefmt='%Y-%m-%d %H:%M:%S') 
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_format)
    stream_handler.setLevel(level)
    logger.addHandler(stream_handler)
    file_handler = logging.handlers.TimedRotatingFileHandler(filename='./logs/application.log',when='midnight')
    file_handler.setFormatter(log_format)
    file_handler.setLevel(level)
    logger.addHandler(file_handler)
    return logger