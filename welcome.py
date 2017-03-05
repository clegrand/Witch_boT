import logging
import argparse

opts = {}
logger = logging.Logger('default')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.ERROR)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', "--create", action="store_true",
                        help=_("Show login section"))
    parser.add_argument('-d', "--debug", action="store_true")
    parser.add_argument('-g', "--no-graphic", dest="graphic", action="store_false", default=True)
    global opts, logger
    opts['args'] = o = parser.parse_args()
    if o.debug:
        logger.setLevel(logging.DEBUG)
    elif not o.graphic:
        logger.setLevel(logging.INFO)
    return o
