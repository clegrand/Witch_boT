#! /usr/bin/env python3

from welcome import get_args
from desk import Window
from printer import Console


if __name__ == "__main__":
    opts = get_args()
    if opts.graphic:
        # TODO : Make graphic interface
        pass
    else:
        c = Console()
        c.connect()
