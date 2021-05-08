import json
from jsonschema import ValidationError
import copy
import itertools
from collections import defaultdict

from reasoner_validator import validate_Message_1_0, validate_Message_1_1, \
        validate_Query_1_0, validate_Query_1_1

from trapi_model.base import TrapiBaseClass
from trapi_model.query_graph import QueryGraph
from trapi_model.knowledge_graph import KnowledgeGraph
from trapi_model.results import Results, Result

def get_supported_biolink_versions():
    from trapi_model.base import TOOLKITS
    return list(TOOLKITS.keys()).remove('latest')

class Query(TrapiBaseClass):
    def __init__(self, trapi_version='1.1', biolink_version=None, max_results=10):
        self.trapi_version = trapi_version
        self.biolink_version = biolink_version
        self.message = Message(trapi_version, biolink_version)
        self.max_results = max_results
        super().__init__(trapi_version, biolink_version)

    def to_dict(self):
        return {
                "message": self.message.to_dict(),
                "max_results": self.max_results,
                "trapi_version": self.trapi_version,
                "biolink_version": self.biolink_version,
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

    @staticmethod
    def load(trapi_version, biolink_version, message):
        new_message = Message(trapi_version, biolink_version)
        query_graph = message.pop("query_graph", None)
        knowledge_graph = message.pop("knowledge_graph", None)
        results = message.pop("results", None)
        if query_graph is not None:
            new_message.query_graph = QueryGraph.load(trapi_version, biolink_version, query_graph)
        if knowledge_graph is not None:
            new_message.knowledge_graph = KnowledgeGraph.load(trapi_version, biolink_version, knowledge_graph)
        if results is not None:
            new_message.results = Results.load(trapi_version, biolink_version, results)
        return new_message

    def update(self, kg, res=None):
        _map = {}
        # Process KG nodes
        for knode_id, knode in kg.nodes.items():
            master_knode_id = self.knowledge_graph.add_node(
                    knode_id,
                    knode.name,
                    categories=knode.categories,
                    )
            if knode.attributes is not None:
                for attribute in knode.attributes:
                    self.knowledge_graph.add_attribute(
                        attribute_type_id=attribute.attribute_type_id,
                        value=attribute.value,
                        value_type_id=attribute.value_type_id,
                        original_attribute_name=attribute.original_attribute_name,
                        attribute_source=attribute.attribute_source,
                        value_url=attribute.value_url,
                        description=attribute.description,
                        node_id=master_knode_id,
                        )
            _map[knode_id] = master_knode_id
        # Process edges
        for kedge_id, kedge in kg.edges.items():
            master_kedge_id = self.knowledge_graph.add_edge(
                    k_object=kedge.object,
                    k_subject=kedge.subject,
                    predicate=kedge.predicate,
                    relation=kedge.relation,
                    )
            if kedge.attributes is not None:
                for attribute in kedge.attributes:
                    self.knowledge_graph.add_attribute(
                        attribute_type_id=attribute.attribute_type_id,
                        value=attribute.value,
                        value_type_id=attribute.value_type_id,
                        original_attribute_name=attribute.original_attribute_name,
                        attribute_source=attribute.attribute_source,
                        value_url=attribute.value_url,
                        description=attribute.description,
                        edge_id=master_kedge_id,
                        )
            _map[kedge_id] = master_kedge_id
        # Process results
        if res is not None:
            for result in res.results:
                # Process node bindings
                new_node_bindings = defaultdict(list)
                for qg_id, node_bindings in result.node_bindings.items():
                    new_kg_ids = [_map[binding.id] for binding in node_bindings]
                    new_node_bindings[qg_id].extend(new_kg_ids)
                new_edge_bindings = defaultdict(list)
                for qg_id, edge_bindings in result.edge_bindings.items():
                    new_kg_ids = [_map[binding.id] for binding in edge_bindings]
                    new_edge_bindings[qg_id].extend(new_kg_ids)
                self.results.add_result(
                        new_node_bindings,
                        new_edge_bindings,
                        )
