import json
import os
from jsonschema import ValidationError
import copy
import itertools
from collections import defaultdict

from chp_utils.generic import dict_replace_value
from reasoner_validator import validate

from trapi_model.base import TrapiBaseClass
from trapi_model.query_graph import QueryGraph
from trapi_model.knowledge_graph import KnowledgeGraph
from trapi_model.results import Results, Result


class Message(TrapiBaseClass):
    def __init__(self, trapi_version='1.2', biolink_version=None):
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

    def find_and_replace(self, old_value, new_value):
        message_dict = self.to_dict()
        replaced_message_dict = dict_replace_value(message_dict, old_value, new_value)
        return Message.load(self.trapi_version, self.biolink_version, replaced_message_dict)

    def validate(self):
        _dict = self.to_dict()
        try:
            validate(_dict, 'Message', self.trapi_version)
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
