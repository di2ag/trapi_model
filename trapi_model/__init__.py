import json
from jsonschema import ValidationError

from reasoner_validator import validate_Message_1_0, validate_Message_1_1, \
        validate_Query_1_0, validate_Query_1_1

from trapi_model.base import TrapiBaseClass
from trapi_model.query_graph import QueryGraph
from trapi_model.knowledge_graph import KnowledgeGraph
from trapi_model.results import Results, Result

def get_supported_biolink_versions():
    from trapi_model.base import TOOLKITS
    return list(TOOLKITS.keys()).remove('latest')

class Query:
    def __init__(self, trapi_version='1.1', biolink_version=None):
        self.trapi_version = trapi_version
        self.biolink_version = biolink_version
        self.message = Message(trapi_version, biolink_version)

    def to_dict(self):
        return {
                "message": self.message.to_dict(),
                }

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

    def load(self, query=None, query_filepath=None):
        if query is None and query_filepath is None:
            return ValueError('Message and Message filepath can not both be None.')
        if query_filepath is not None:
            if query is not None:
                return ValueError('You passed in both a filepath and query object.')
            with open(query_filepath, 'r') as f_:
                query = json.load(f_)
        message = query.pop("message", None)
        if message is not None:
            self.message.load(message)
        return self

class Message(TrapiBaseClass):
    def __init__(self, trapi_version='1.1', biolink_version=None):
        self.trapi_version = trapi_version
        self.biolink_version = biolink_version
        self.query_graph = QueryGraph(trapi_version, biolink_version)
        self.knowledge_graph = KnowledgeGraph(trapi_version, biolink_version)
        self.results = Results(trapi_version, biolink_version)

    def to_dict(self):
        return {
                "query_graph": self.query_graph.to_dict(),
                "knowledge_graph": self.knowledge_graph.to_dict(),
                "results": self.results.to_dict(),
                }

    def validate(self):
        _dict = self.to_dict()
        try:
            if self.trapi_version == '1.0':
                validate_Message_1_0(_dict)
            elif self.trapi_version == '1.1':
                validate_Message_1_1(_dict)
            else:
                raise UnsupportedTrapiVersion(self.trapi_version)
            return True, None 
        except ValidationError as ex:
            return False, ex.message

    def load(self, message):
        query_graph = message.pop("query_graph", None)
        knowledge_graph = message.pop("knowledge_graph", None)
        results = message.pop("results", None)
        if query_graph is not None:
            self.query_graph.load(query_graph)
        if knowledge_graph is not None:
            self.knowledge_graph.load(knowledge_graph)
        if results is not None:
            self.results.load(results)
        return self
