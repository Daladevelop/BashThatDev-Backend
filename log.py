#!/usr/bin/python -tt
# -*- coding: utf-8 -*-
# vim: ts=4:et:

"""
Logging module for handling logging!

Author: Christofer Odén <bei.oden@gmail.com>

"""

import logging

def initialize_logging(debug=False):
    if debug:
        level = logging.DEBUG
    else:
        level = logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(module)s:%(lineno)d %(message)s")

# Runs tests if module is executed directly
if __name__ == "__main__":
    initialize_logging(True)
    log = logging.getLogger(__name__)
    log.debug("Debug message")
    log.info("Info message")
