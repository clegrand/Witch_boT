import logging
import argparse

opts = argparse.Namespace()
logger = logging.Logger('default')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.ERROR)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', "--debug", action="store_true")
    parser.add_argument('-g', "--no-graphic", dest="graphic", action="store_false", default=True)
    global opts, logger
    opts = parser.parse_args()
    if opts.debug:
        logger.setLevel(logging.DEBUG)
    elif not opts.graphic:
        logger.setLevel(logging.INFO)
    return opts
