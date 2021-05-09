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
import time
from collections import defaultdict

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)


class TestLoading(unittest.TestCase):
    def test_set_biolink_version(self):
        import trapi_model
        # Test latest
        versions = ['latest', '1.8.2']
        for version in versions:
            trapi_model.set_biolink_version(version)
            import trapi_model.biolink
            self.assertEqual(trapi_model.biolink.BIOLINK_VERSION, version)

    def test_set_biolink_debug_mode(self):
        import trapi_model
        trapi_model.set_biolink_debug_mode(True)
        start_time = time.time()
        from trapi_model.biolink.constants import BIOLINK_GENE_ENTITY
        self.assertLess(time.time()-start_time, 10)
        self.assertTrue(BIOLINK_GENE_ENTITY.get_curie(), 'biolink:Gene')

class TestBiolinkEntity(unittest.TestCase):
    
    def test_inverse(self):
        from trapi_model.biolink.constants import BIOLINK_TREATS_ENTITY
        self.assertEqual(BIOLINK_TREATS_ENTITY.get_curie(), 'biolink:treats')
        self.assertEqual(BIOLINK_TREATS_ENTITY.get_inverse().get_curie(), 'biolink:treated_by')

    def test_get_ancestors(self):
        from trapi_model.biolink.constants import BIOLINK_GENE_ENTITY
        self.assertEqual(BIOLINK_GENE_ENTITY.get_curie(), 'biolink:Gene')
        self.assertListEqual(
                [
                    'biolink:GenomicEntity',
                    'biolink:MolecularEntity',
                    'biolink:BiologicalEntity',
                    'biolink:NamedThing',
                    'biolink:Entity'
                    ],
                [entity.get_curie() for entity in BIOLINK_GENE_ENTITY.get_ancestors()],
                )

    def test_inverse_debug_mode(self):
        import trapi_model
        trapi_model.set_biolink_debug_mode(True)
        from trapi_model.biolink.constants import BIOLINK_TREATS_ENTITY
        self.assertEqual(BIOLINK_TREATS_ENTITY.get_curie(), 'biolink:treats')
        self.assertEqual(BIOLINK_TREATS_ENTITY.get_inverse().get_curie(), 'biolink:treated_by')
        
    def test_get_ancestors_debug_mode(self):
        import trapi_model
        trapi_model.set_biolink_debug_mode(True)
        from trapi_model.biolink.constants import BIOLINK_GENE_ENTITY
        self.assertEqual(BIOLINK_GENE_ENTITY.get_curie(), 'biolink:Gene')
        self.assertListEqual(
                [
                    'biolink:GenomicEntity',
                    'biolink:MolecularEntity',
                    'biolink:BiologicalEntity',
                    'biolink:NamedThing',
                    'biolink:Entity'
                    ],
                [entity.get_curie() for entity in BIOLINK_GENE_ENTITY.get_ancestors()],
                )

class TestNcatsRepo(unittest.TestCase):
    def setUp(self):
        self.ncats_test_dir = os.path.abspath('../submodules/ncats_testing')

    def test_ars_predicates_queries(self):
        from trapi_model.query import Query
        from trapi_model.exceptions import UnknownBiolinkEntity
        ars_predicates_dir = os.path.join(self.ncats_test_dir, 'ars-requests/predicates')
        # Run tests
        for filename in os.listdir(ars_predicates_dir):
            try:
                if os.path.splitext(filename)[-1] == '.json':
                    filepath = os.path.join(ars_predicates_dir, filename)
                    query = Query.load('1.0', None, query_filepath=filepath)
                    query_dict = query.to_dict()
                    #print(json.dumps(query_dict, indent=2))
                    if query.is_batch_query():
                        batch = query.expand_batch_query()
            except UnknownBiolinkEntity as ex:
                logger.critical('Failed on file {} with {}'.format(filename, ex.message))

    def test_ars_musthave_queries(self):
        from trapi_model.query import Query
        from trapi_model.exceptions import UnknownBiolinkEntity
        ars_predicates_dir = os.path.join(self.ncats_test_dir, 'ars-requests/must-have')
        # Run tests
        for filename in os.listdir(ars_predicates_dir):
            try:
                if os.path.splitext(filename)[-1] == '.json':
                    filepath = os.path.join(ars_predicates_dir, filename)
                    query = Query.load('1.0', None, query_filepath=filepath)
                    _ = query.to_dict()
                    # Test if its a batch query and if so extract
                    if query.is_batch_query():
                        batch = query.expand_batch_query()
            except UnknownBiolinkEntity as ex:
                logger.critical('Failed on file {} with {}'.format(filename, ex.message))
    
    def test_ars_notnone_queries(self):
        from trapi_model.query import Query
        from trapi_model.exceptions import UnknownBiolinkEntity
        ars_predicates_dir = os.path.join(self.ncats_test_dir, 'ars-requests/not-none')
        # Run tests
        for filename in os.listdir(ars_predicates_dir):
            try:
                if os.path.splitext(filename)[-1] == '.json':
                    filepath = os.path.join(ars_predicates_dir, filename)
                    query = Query.load('1.0', None, query_filepath=filepath)
                    query_dict = query.to_dict()
                    if query.is_batch_query():
                        batch = query.expand_batch_query()
            except UnknownBiolinkEntity as ex:
                logger.critical('Failed on file {} with {}'.format(filename, ex.message))
