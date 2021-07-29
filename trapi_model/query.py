import json
import os
import uuid
from jsonschema import ValidationError
import copy
import itertools
from collections import defaultdict

from reasoner_validator import validate_Query_1_0, validate_Query_1_1

from trapi_model.base import TrapiBaseClass
from trapi_model.message import Message
from trapi_model.logger import Logger

class Query(TrapiBaseClass):
    def __init__(self, trapi_version='1.1', biolink_version=None, max_results=10, q_id=None):
        self.trapi_version = trapi_version
        self.biolink_version = biolink_version
        self.message = Message(trapi_version, biolink_version)
        self.max_results = max_results
        self.logger = Logger()
        self.id = q_id
        if q_id is None:
            self.id = str(uuid.uuid4())
        super().__init__(trapi_version, biolink_version)

    def to_dict(self):
        return {
                "message": self.message.to_dict(),
                "max_results": self.max_results,
                "trapi_version": self.trapi_version,
                "biolink_version": self.biolink_version,
                "logs": self.logger.to_dict(),
                "pk": self.id,
                }
    
    def find_and_replace(self, old_value, new_value):
        self.message = self.message.find_and_replace(old_value, new_value)
    
    def info(self, message, code=None):
        self.logger.info(message, code)
    
    def debug(self, message, code=None):
        self.logger.debug(message, code)
    
    def warning(self, message, code=None):
        self.logger.warning(message, code)
    
    def error(self, message, code=None):
        self.logger.error(message, code)

    def validate(self):
        _dict = self.to_dict()
        try:
            if self.trapi_version == '1.0':
                validate_Query_1_0(_dict)
            elif self.trapi_version == '1.1':
                validate_Query_1_1(_dict)
            else:
                raise UnsupportedTrapiVersion(self.trapi_version)
            return True, None 
        except ValidationError as ex:
            return False, ex.message

    @staticmethod
    def load(trapi_version, biolink_version, query=None, query_filepath=None):
        if query is None and query_filepath is None:
            return ValueError('Message and Message filepath can not both be None.')
        if query_filepath is not None:
            if query is not None:
                return ValueError('You passed in both a filepath and query object.')
            with open(query_filepath, 'r') as f_:
                query = json.load(f_)
        new_query = Query(trapi_version, biolink_version)
        message = query.pop("message", None)
        if message is not None:
            new_query.message = Message.load(
                    trapi_version,
                    biolink_version,
                    message=message,
                    )
        return new_query

    def is_batch_query(self):
        query_graph = self.message.query_graph
        # Check for a batch node
        for _, node_info in query_graph.nodes.items():
            if node_info.ids is not None:
                if len(node_info.ids) > 1:
                    return True
            if node_info.categories is not None:
                if len(node_info.categories) > 1:
                    return True
        # Check edges
        for _, edge_info in query_graph.edges.items():
            if edge_info.predicates is not None:
                if len(edge_info.predicates) > 1:
                    return True
        return False

    def get_copy(self):
        return Query.load(self.trapi_version, self.biolink_version, query=self.to_dict())

    def expand_batch_query(self):
        query_graph = self.message.query_graph
        options = []
        options_map = []
        # Get batch nodes
        for node_id, node_info in query_graph.nodes.items():
            if node_info.ids is not None:
                if len(node_info.ids) > 1:
                    options_map.append((node_id, 'ids'))
                    options.append(node_info.ids)
            if node_info.categories is not None:
                if len(node_info.categories) > 1:
                    options_map.append((node_id, 'categories')) 
                    options.append(node_info.categories)
        # Get batch edges
        for edge_id, edge_info in query_graph.edges.items():
            if edge_info.predicates is not None:
                if len(edge_info.predicates) > 1:
                    options_map.append((edge_id, 'predicates'))
                    options.append(edge_info.predicates)
        # Build single queries
        extracted_queries = []
        for query_config in itertools.product(*options):
            # Deepcopy workaround
            new_query = self.get_copy()
            for idx, option_label in enumerate(options_map):
                q_label, attribute = option_label
                if attribute == 'predicates':
                    new_query.message.query_graph.edges[q_label].set_predicates(query_config[idx])
                elif attribute == 'ids':
                    new_query.message.query_graph.nodes[q_label].set_ids(query_config[idx])
                elif attribute == 'categories':
                    new_query.message.query_graph.nodes[q_label].set_categories(query_config[idx])
                else:
                    raise ValueError('Unknown attribute label: {}'.format(attribute))
            extracted_queries.append(new_query)
        return extracted_queries
