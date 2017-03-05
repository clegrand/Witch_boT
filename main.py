#! /usr/bin/env python3

import gettext

from welcome import get_args
from desk import Window
from printer import Console


if __name__ == "__main__":
    gettext.install('Witch_boT')
    opts = get_args()
    if opts.graphic:
        # TODO : Make graphic interface
        pass
    else:
        c = Console()
        c.connect()
