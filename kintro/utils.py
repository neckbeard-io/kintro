import logging
import sys


def _init_logger(name):
    formatter = logging.Formatter(
        fmt=(
            '%(asctime)s %(filename)-15s %(funcName)-20s '
            '%(levelname)-7s %(message)s'
        ),
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(screen_handler)

    return logger