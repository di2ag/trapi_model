"""
    Source code developed by DI2AG.
    Thayer School of Engineering at Dartmouth College
    Authors:    Dr. Eugene Santos, Jr
                Mr. Chase Yakaboski,
                Mr. Gregory Hyde,
                Mr. Luke Veenhuis,
                Dr. Keum Joo Kim
"""

import unittest
import json
import logging
import sys
import os
from collections import defaultdict

from trapi_model import Query
from trapi_model.exceptions import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class TestNcatsRepo(unittest.TestCase):
    def setUp(self):
        self.ncats_test_dir = os.path.abspath('../submodules/ncats_testing')

    def test_ars_predicates_queries(self):
        ars_predicates_dir = os.path.join(self.ncats_test_dir, 'ars-requests/predicates')
        # Run tests
        for filename in os.listdir(ars_predicates_dir):
            try:
                if os.path.splitext(filename)[-1] == '.json':
                    filepath = os.path.join(ars_predicates_dir, filename)
                    query = Query('1.0').load(query_filepath=filepath)
            except UnknownBiolinkEntity as ex:
                logger.critical('Failed on file {} with {}'.format(filename, ex.message))

    def test_ars_musthave_queries(self):
        ars_predicates_dir = os.path.join(self.ncats_test_dir, 'ars-requests/must-have')
        # Run tests
        for filename in os.listdir(ars_predicates_dir):
            try:
                if os.path.splitext(filename)[-1] == '.json':
                    filepath = os.path.join(ars_predicates_dir, filename)
                    query = Query('1.0').load(query_filepath=filepath)
            except UnknownBiolinkEntity as ex:
                logger.critical('Failed on file {} with {}'.format(filename, ex.message))
    
    def test_ars_notnone_queries(self):
        ars_predicates_dir = os.path.join(self.ncats_test_dir, 'ars-requests/not-none')
        # Run tests
        for filename in os.listdir(ars_predicates_dir):
            try:
                if os.path.splitext(filename)[-1] == '.json':
                    filepath = os.path.join(ars_predicates_dir, filename)
                    query = Query('1.0').load(query_filepath=filepath)
            except UnknownBiolinkEntity as ex:
                logger.critical('Failed on file {} with {}'.format(filename, ex.message))
