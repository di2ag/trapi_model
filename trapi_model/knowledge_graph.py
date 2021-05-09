
"""
TRAPI Knowedge Graph Data Classes
"""
import sys
import json
from jsonschema import ValidationError

from trapi_model.biolink.constants import get_biolink_entity
from trapi_model.biolink import BiolinkEntity
from trapi_model.exceptions import *
from trapi_model.base import TrapiBaseClass

from reasoner_validator import validate_Edge_1_0, validate_Edge_1_1, \
validate_Node_1_0, validate_Node_1_1, validate_KnowledgeGraph_1_0, validate_KnowledgeGraph_1_1


class Attribute(TrapiBaseClass):
    def __init__(self,
            trapi_version,
            biolink_version,
            attribute_type_id=None,
            value=None,
            value_type_id=None,
            original_attribute_name=None,
            attribute_source=None,
            value_url=None,
            description=None,
            ):
        self.attribute_type_id = attribute_type_id
        self.value = value
        self.value_type_id = value_type_id
        self.original_attribute_name = original_attribute_name
        self.attribute_source = attribute_source
        self.value_url = value_url
        self.description = description
        super().__init__(trapi_version, biolink_version)

    def to_dict(self):
        if self.trapi_version == '1.0':
            return {
                        "name": self.original_attribute_name,
                        "value": self.value,
                        "type": self.attribute_type_id,
                        "url": self.value_url,
                        "source": self.attribute_source,
                    }
        elif self.trapi_version == '1.1':
            return {
                        "attribute_type_id": self.attribute_type_id,
                        "original_attribute_name": self.original_attribute_name,
                        "value": self.value,
                        "value_type_id": self.value_type_id,
                        "attribute_source": self.attribute_source,
                        "value_url": self.value_url,
                        "description": self.description,
                    }
        else:
            raise UnsupportedTrapiVersion(self.trapi_version)

    @staticmethod
    def load(trapi_version, biolink_version, attribute_info, name=None):
        if trapi_version == '1.0':
            attribute = Attribute(
                    trapi_version,
                    biolink_version,
                    attribute_type_id=attribute_info.pop("type"),
                    value=attribute_info.pop("value"),
                    original_attribute_name=attribute_info.pop("name", None),
                    attribute_source=attribute_info.pop("source", None),
                    value_url=attribute_info.pop("url", None),
                    )
        elif trapi_version == '1.1':
            attribute = Attribute(
                    trapi_version,
                    biolink_version,
                    attribute_type_id=attribute_info.pop("attribute_type_id"),
                    value=attribute_info.pop("value"),
                    value_type_id=attribute_info.pop("value_type_id", None),
                    original_attribute_name=attribute_info.pop("original_attribute_name", None),
                    attribute_source=attribute_info.pop("attribute_source", None),
                    value_url=attribute_info.pop("value_url", None),
                    description=attribute_info("description", None),
                    )
        return attribute

class KNode(TrapiBaseClass):
    def __init__(self,
            trapi_version,
            biolink_version,
            name = None,
            categories = None,
            attributes = None,
            ):
        self.name = name 
        if type(categories) is not list and categories is not None:
            categories = [categories]
        self.categories = categories
        if attributes is None:
            self.attributes = []
        else:
            self.attributes = attributes
        super().__init__(trapi_version, biolink_version)

        valid, message = self.validate()
        if not valid:
            raise InvalidTrapiComponent(trapi_version, 'KNode', message)

    def to_dict(self):
        categories = self.categories
        if categories is not None:
            categories = [category.get_curie() for category in categories]
        if self.trapi_version == '1.0':
            _dict = {
                        "name": self.name,
                        "category": categories,
                        "attributes": [],
                    }
        elif self.trapi_version == '1.1':
            _dict = {
                        "name": self.name,
                        "categories": categories,
                        "attributes": []
                    }
        else:
            raise UnsupportedTrapiVersion(self.trapi_version)
        if self.attributes is not None:
            for attribute in self.attributes:
                _dict["attributes"].append(attribute.to_dict())
        return _dict
    
    def set_categories(self, categories):
        if type(categories) is str:
            self.categories = [get_biolink_entity(categories)]
        elif type(categories) is BiolinkEntity:
            self.categories = [categories]
        else:
            _categories = []
            for category in categories:
                if type(category) is str:
                    _categories.append(get_biolink_entity(category))
                elif type(category) is BiolinkEntity:
                    _categories.append(category)
            self.categories = _categories

    @staticmethod
    def load(trapi_version, biolink_version, knode_info):
        knode = KNode(trapi_version, biolink_version)
        if trapi_version == '1.0':
            categories = knode_info.pop("category", None)
            if categories is not None:
                knode.set_categories(categories)
        elif trapi_version == '1.1':
            categories = knode_info.pop("categories", None)
            if categories is not None:
                knode.set_categories(categories)
        knode.name = knode_info.pop("name", None)
        attributes = knode_info.pop("attributes", None)
        if attributes is not None:
            for attribute_info in attributes:
                knode.attributes.append(
                        Attribute.load(
                            trapi_version, 
                            biolink_version,
                            attribute_info,
                            )
                        )
        valid, message = knode.validate()
        if valid:
            return knode
        else:
            raise InvalidTrapiComponent(trapi_version, 'KNode', message)

    def add_attribute(self, 
            attribute_type_id,
            value,
            value_type_id=None,
            original_attribute_name=None,
            attribute_source=None,
            value_url=None,
            description=None,
            ):
        if self.attributes is None:
            self.attributes = []
        self.attributes.append(
                Attribute(
                    trapi_version=self.trapi_version,
                    biolink_version=self.biolink_version,
                    attribute_type_id=attribute_type_id,
                    value=value,
                    value_type_id=value_type_id,
                    original_attribute_name=original_attribute_name,
                    attribute_source=attribute_source,
                    value_url=value_url,
                    description=description,
                    )
                )
        valid, message = self.validate()
        if not valid:
            raise InvalidTrapiComponent(self.trapi_version, 'KNode', message)

    def validate(self):
        _dict = self.to_dict()
        try:
            if self.trapi_version == '1.0':
                validate_Node_1_0(_dict)
            elif self.trapi_version == '1.1':
                validate_Node_1_1(_dict)
            else:
                raise UnsupportedTrapiVersion(self.trapi_version)
            return True, None 
        except ValidationError as ex:
                return False, ex.message

class KEdge(TrapiBaseClass):
    def __init__(self,
            trapi_version,
            biolink_version,
            k_subject,
            k_object,
            predicate=None,
            relation=None,
            attributes=None,
            ):
        self.subject = k_subject
        self.object = k_object
        self.predicate = predicate
        self.relation = relation
        if attributes is None:
            self.attributes = []
        else:
            self.attributes = attributes
        super().__init__(trapi_version, biolink_version)
        
        valid, message = self.validate()
        if not valid:
            raise InvalidTrapiComponent(trapi_version, 'KEdge', message)

    def to_dict(self):
        if self.trapi_version == '1.0' or self.trapi_version == '1.1':
            predicate = self.predicate
            if predicate is not None:
                predicate = predicate.get_curie()
            _dict = {
                    "predicate": predicate,
                    "relation": self.relation,
                    "subject": self.subject,
                    "object": self.object,
                    }
            if self.attributes is not None:
                _dict["attributes"] = []
                for attribute in self.attributes:
                    _dict["attributes"].append(attribute.to_dict())
            return _dict
        else:
            raise UnsupportedTrapiVersion(self.trapi_version)

    @staticmethod
    def load(trapi_version, biolink_version, kedge_info):
        kedge = KEdge(
                trapi_version,
                biolink_version,
                kedge_info.pop("subject"),
                kedge_info.pop("object"),
                )
        predicate = kedge_info.pop("predicate", None)
        if predicate is not None:
            kedge.predicate = get_biolink_entity(predicate)
        kedge.relation = kedge_info.pop("relation", None)
        attributes = kedge_info.pop("attributes", None)
        if attributes is not None:
            for attribute_info in attributes:
                kedge.attributes.append(
                        Attribute.load(
                            trapi_version,
                            biolink_version,
                            attribute_info,
                            )
                        )
        valid, message = kedge.validate()
        if valid:
            return kedge
        else:
            raise InvalidTrapiComponent(trapi_version, 'KEdge', message)
        return kedge
    
    def add_attribute(self, 
            attribute_type_id,
            value,
            value_type_id=None,
            original_attribute_name=None,
            attribute_source=None,
            value_url=None,
            description=None,
            ):
        if self.attributes is None:
            self.attributes = []
        self.attributes.append(
                Attribute(
                    trapi_version=self.trapi_version,
                    biolink_version=self.biolink_version,
                    attribute_type_id=attribute_type_id,
                    value=value,
                    value_type_id=value_type_id,
                    original_attribute_name=original_attribute_name,
                    attribute_source=attribute_source,
                    value_url=value_url,
                    description=description,
                    )
                )
        valid, message = self.validate()
        if not valid:
            raise InvalidTrapiComponent(self.trapi_version, 'QEdge', message)
        
    def validate(self):
        _dict = self.to_dict()
        try:
            if self.trapi_version == '1.0':
                validate_Edge_1_0(_dict)
            elif self.trapi_version == '1.1':
                validate_Edge_1_1(_dict)
            else:
                raise UnsuppoertedTrapiVersion(self.trapi_version)
            return True, None 
        except ValidationError as ex:
                return False, ex.message

class KnowledgeGraph(TrapiBaseClass):
    def __init__(self, trapi_version='1.1', biolink_version=None):
        self.nodes = {}
        self.edges = {}
        self.node_counter = 0
        self.edge_counter = 0
        super().__init__(trapi_version, biolink_version)

    def add_node(self, curie, name, categories):
        # Run categories through Biolink
        if type(categories) is not list and categories is not None:
            categories = [BiolinkEntity(categories, biolink_version=self.biolink_version)]
        elif categories is not None:
            _categories = []
            for category in categories:
                if type(category) is BiolinkEntity:
                    _categories.append(category)
                else:
                    _categories.append(BiolinkEntity(category, biolink_version=self.biolink_version))
            categories = _categories
        self.node_counter += 1
        self.nodes[curie] = KNode(
                trapi_version=self.trapi_version,
                biolink_version=self.biolink_version,
                name=name,
                categories=categories
                )
        return curie

    def add_edge(self, k_subject, k_object, predicate=None, relation=None):
        # Run predicates through Biolink
        if type(predicate) is not BiolinkEntity:
            predicate = BiolinkEntity(predicate, biolink_version=self.biolink_version)
        edge_id = 'e{}'.format(self.edge_counter)
        self.edge_counter += 1
        self.edges[edge_id] = KEdge(
                trapi_version=self.trapi_version,
                biolink_version=self.biolink_version,
                k_subject=k_subject,
                k_object=k_object,
                predicate=predicate,
                relation=relation,
                )
        return edge_id

    def add_attribute(self,
            attribute_type_id,
            value,
            value_type_id=None,
            original_attribute_name=None,
            attribute_source=None,
            value_url=None,
            description=None,
            edge_id=None,
            node_id=None,
            ):
        if edge_id is None and node_id is None:
            raise ValueError('Must specify either node or edge id.')
        elif edge_id is not None and node_id is not None:
            raise ValueError('Must specify either node or edge id, not both.')
        if edge_id is not None:
            q_obj = self.edges[edge_id]
        else:
            q_obj = self.nodes[node_id]
        q_obj.add_attribute(
            attribute_type_id=attribute_type_id,
            value=value,
            value_type_id=value_type_id,
            original_attribute_name=original_attribute_name,
            attribute_source=attribute_source,
            value_url=value_url,
            description=description,
                )
        return True

    def to_dict(self):
        nodes = {}
        edges = {}
        for node_id, node in self.nodes.items():
            nodes[node_id] = node.to_dict()
        for edge_id, edge in self.edges.items():
            edges[edge_id] = edge.to_dict()
        return {
                "nodes": nodes,
                "edges": edges,
                }

    def find_nodes(self, categories=None, ids=None):
        matched_node_ids = []
        for node_id, node_info in self.nodes.items():
            if categories is not None:
                if node_info.categories != categories:
                    continue
            if ids is not None:
                if node_info.ids != ids:
                    continue
            matched_node_ids.append(node_id)
        return matched_node_ids

    def validate(self):
        _dict = self.to_dict()
        try:
            if self.trapi_version == '1.0':
                validate_KnowledgeGraph_1_0(_dict)
            elif self.trapi_version == '1.1':
                validate_KnowledgeGraph_1_1(_dict)
            else:
                raise UnsuppoertedTrapiVersion(self.trapi_version)
            return True, None 
        except ValidationError as ex:
            return False, ex.message

    @staticmethod
    def load(trapi_version, biolink_version, knowledge_graph):
        new_knowledge_graph = KnowledgeGraph(trapi_version, biolink_version)
        # Load Nodes
        for node_id, node_info in knowledge_graph["nodes"].items():
            new_knowledge_graph.nodes[node_id] = KNode.load(
                    trapi_version,
                    biolink_version,
                    node_info,
                    )
        # Load Edges
        for edge_id, edge_info in knowledge_graph["edges"].items():
            new_knowledge_graph.edges[edge_id] = KEdge.load(
                    trapi_version,
                    biolink_version,
                    edge_info,
                    )
        valid, message = new_knowledge_graph.validate()
        if valid:
            return new_knowledge_graph
        else:
            raise InvalidTrapiComponent(trapi_version, 'KnowledgeGraph', message)
        
