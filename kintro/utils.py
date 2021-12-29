import logging
import sys


def _init_logger(name, log_level):
    
    fmt = '%(asctime)s %(filename)-15s %(funcName)-20s ' \
          '%(levelname)-7s %(message)s'
    
    if log_level == logging.DEBUG:
        fmt = '%(asctime)s %(filename)-15s %(funcName)-20s ' \
              '%(threadName)-23s %(levelname)-7s %(message)s'
    
    formatter = logging.Formatter(
        fmt=(fmt),
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.addHandler(screen_handler)

    return logger
