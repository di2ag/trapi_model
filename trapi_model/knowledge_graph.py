
"""
TRAPI Knowedge Graph Data Classes
"""

import json
from jsonschema import ValidationError

from trapi_model.constants import *
from trapi_model.exceptions import *
from trapi_model.base import TrapiBaseClass, BiolinkEntity

from reasoner_validator import validate_Edge_1_0, validate_Edge_1_1, \
validate_Node_1_0, validate_Node_1_1, validate_KnowledgeGraph_1_0, validate_KnowledgeGraph_1_1
from bmt import Toolkit


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

    def load(self, attribute_info, name=None):
        if self.trapi_version == '1.0':
            self.attribute_type_id = attribute_info.pop("type")
            self.value = attribute_info.pop("value")
            self.original_attribute_name = attribute_info.pop("name", None)
            self.attribute_source = attribute_info.pop("source", None)
            self.value_url = attribute_info.pop("url", None)
        elif self.trapi_version == '1.1':
            self.attribute_type_id = attribute_info.pop("attribute_type_id")
            self.value = attribute_info.pop("value")
            self.value_type_id = attribute_info.pop("value_type_id", None)
            self.original_attribute_name = attribute_info.pop("original_attribute_name", None)
            self.attribute_source = attribute_info.pop("attribute_source", None)
            self.value_url = attribute_info.pop("value_url", None)
            self.description = attribute_info("description", None)
        return self

class KNode(TrapiBaseClass):
    def __init__(self,
            trapi_version,
            biolink_version,
            name = None,
            categories = None,
            attributes = None,
            ):
        self.name = name 
        self.categories = categories
        self.attributes = attributes
        super().__init__(trapi_version, biolink_version)

        valid, message = self.validate()
        if not valid:
            raise InvalidTrapiComponent(trapi_version, 'KNode', message)

    def to_dict(self):
        if self.trapi_version == '1.0':
            _dict = {
                        "name": self.name,
                        "category": self.categories.get_curie(),
                        "attributes": [],
                    }
        elif self.trapi_version == '1.1':
            categories = self.categories
            if type(categories) is not list and categories is not None:
                categories = [categories]
            _dict = {
                        "name": self.name,
                        "categories": [category.get_curie() for category in categories],
                        "attributes": []
                    }
        else:
            raise UnsupportedTrapiVersion(self.trapi_version)
        if self.attributes is not None:
            for attribute in self.attributes:
                _dict["attributes"].append(attribute.to_dict())
        return _dict

    def load(self, knode_info):
        if self.trapi_version == '1.0':
            self.categories = knode_info.pop("category", None)
        elif self.trapi_version == '1.1':
            self.categories = knode_info.pop("categories", None)
        self.name = knode_info.pop("name", None)
        attributes = knode_info.pop("attributes", None)
        if attributes is not None:
            for attribute_info in attributes:
                _attribute = Attribute(
                        trapi_version=self.trapi_version, 
                        biolink_version=self.biolink_version,
                        )
                self.attributes.append(_attribute.load(attribute_info))
        valid, message = self.validate()
        if valid:
            return self
        else:
            raise InvalidTrapiComponent(self.trapi_version, 'KNode', message)
        return self

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
            raise InvalidTrapiComponent(trapi_version, 'KNode', message)

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
        self.attributes = attributes
        super().__init__(trapi_version, biolink_version)
        
        valid, message = self.validate()
        if not valid:
            raise InvalidTrapiComponent(trapi_version, 'KEdge', message)

    def to_dict(self):
        if self.trapi_version == '1.0' or self.trapi_version == '1.1':
            _dict = {
                    "predicate": self.predicate.get_curie(),
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

    def load(self, kedge_info):
        self.subject = kedge_info.pop("subject")
        self.object = kedge_info.pop("object")
        self.predicate = kedge_info.pop("predicate", None)
        self.relation = kedge_info.pop("relation", None)
        attributes = kedge_info.pop("attributes", None)
        if attributes is not None:
            for attribute_info in attributes:
                _attribute = Attribute(
                        trapi_version=self.trapi_version,
                        biolink_version=self.biolink_version,
                        )
                self.attributes.append(_attribute.load(attribute_info))
        valid, message = self.validate()
        if valid:
            return self
        else:
            raise InvalidTrapiComponent(self.trapi_version, 'KEdge', message)
        return self
    
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

    def add_node(self, name, categories):
        # Run categories through Biolink
        if type(categories) is not list and categories is not None:
            categories = BiolinkEntity(categories)
        elif categories is not None:
            categories = [BiolinkEntity(category) for category in categories]
        node_id = 'n{}'.format(self.node_counter)
        self.node_counter += 1
        self.nodes[node_id] = QNode(
                trapi_version=self.trapi_version,
                biolink_version=self.biolink_version,
                name=name,
                categories=categories
                )
        return node_id

    def add_edge(self, q_subject, q_object, predicate=None, relation=None):
        # Run predicates through Biolink
        predicate = BiolinkEntity(predicate)
        edge_id = 'e{}'.format(self.edge_counter)
        self.edge_counter += 1
        self.edges[edge_id] = QEdge(
                trapi_version=self.trapi_version,
                biolink_version=self.biolink_version,
                q_subject=q_subject,
                q_object=q_object,
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

    def load(self, knowledge_graph):
        # Load Nodes
        for node_id, node_info in knowledge_graph["nodes"].items():
            _node = KNode(trapi_version=self.trapi_version, biolink_version=self.biolink_version)
            self.nodes[node_id] = _node.load(node_info)
        # Load Edges
        for edge_id, edge_info in knowledge_graph["edges"].items():
            _edge = KEdge(trapi_version=self.trapi_version, biolink_version=self.biolink_version)
            self.edges[edge_id] = _edge.load(edge_info)
        valid, message = self.validate()
        if valid:
            return self
        else:
            raise InvalidTrapiComponent(self.trapi_version, 'KnowledgeGraph', message)
        return self
        
