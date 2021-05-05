"""
TRAPI Query Graph Data Classes
"""

import json
from jsonschema import ValidationError

from trapi_model.constants import *
from trapi_model.exceptions import *
from trapi_model.base import TrapiBaseClass, BiolinkEntity

from reasoner_validator import validate_QEdge_1_0, validate_QEdge_1_1, \
validate_QNode_1_0, validate_QNode_1_1, validate_QueryGraph_1_0, validate_QueryGraph_1_1

class QConstraintOrAdditionalProperty(TrapiBaseClass):
    def __init__(self,
            trapi_version,
            biolink_version,
            name=None,
            c_id=None,
            operator=None,
            value=None,
            unit_id=None,
            unit_name=None,
            c_not=False,
            ):
        self.name = name
        self.id = c_id
        self.operator = operator
        self.value = value
        self.unit_id = unit_id
        self.unit_name = unit_name
        self.c_not = c_not
        super().__init__(trapi_version, biolink_version)

    def to_dict(self):
        if self.trapi_version == '1.0':
            return {
                    self.name: {
                        "id": self.id,
                        "operator": self.operator,
                        "value": self.value,
                        "unit_id": self.unit_id,
                        "unit_name": self.unit_name,
                        }
                    }
        elif self.trapi_version == '1.1':
            return {
                        "name": self.name,
                        "id": self.id,
                        "operator": self.operator,
                        "value": self.value,
                        "unit_id": self.unit_id,
                        "unit_name": self.unit_name,
                        "not": self.c_not,
                    }
        else:
            raise UnsupportedTrapiVersion(self.trapi_version)

    def load(self, constraint_info, name=None):
        if self.trapi_version == '1.0':
            self.name = name
            self.id = constraint_info.pop("id")
            self.operator = constraint_info.pop("operator")
            self.value = constraint_info.pop("value")
            self.unit_id = constraint_info.pop("unit_id", None)
            self.unit_name = constraint_info.pop("unit_name", None)
        elif self.trapi_version == '1.1':
            self.name = constraint_info.pop("name")
            self.id = constraint_info.pop("id")
            self.operator = constraint_info.pop("operator")
            self.value = constraint_info.pop("value")
            self.unit_id = constraint_info.pop("unit_id", None)
            self.unit_name = constraint_info.pop("unit_name", None)
            self.c_not = constraint_info.pop("not", False)
        return self

class QNode(TrapiBaseClass):
    def __init__(self,
            trapi_version,
            biolink_version,
            ids = None,
            categories = None,
            constraints = [],
            ):
        self.ids = ids
        self.categories = categories
        self.constraints = constraints
        super().__init__(trapi_version, biolink_version)

        valid, message = self.validate()
        if not valid:
            raise InvalidTrapiComponent(trapi_version, 'QNode', message)

    def to_dict(self):
        if self.trapi_version == '1.0':
            category = self.categories
            if category is not None:
                category = category.get_curie()
            _dict = {
                        "id": self.ids,
                        "category": category,
                    }
            if self.constraints is not None:
                for constraint in self.constraints:
                    _dict.update(constraint.to_dict())
            return _dict
        elif self.trapi_version == '1.1':
            ids = self.ids
            categories = self.categories
            if type(ids) is not list and ids is not None:
                ids = [ids]
            if type(categories) is not list and categories is not None:
                categories = [categories]
            elif type(categories) is list:
                categories = [category.get_curie() for category in categories]
            _dict = {
                        "ids": ids,
                        "categories": categories,
                        "constraints": []
                    }
            if self.constraints is not None:
                for constraint in self.constraints:
                    _dict["constraints"].append(constraint.to_dict())
            return _dict
        else:
            raise UnsupportedTrapiVersion(self.trapi_version)

    def load(self, node_info):
        if self.trapi_version == '1.0':
            self.ids = node_info.pop("id", None)
            categories = node_info.pop("category", None)
            # Process category
            if categories is not None:
                self.categories = BiolinkEntity(categories)
            # Process constraints
            for name, constraint_info in node_info.items():
                _constraint = QConstraintOrAdditionalProperty(
                        trapi_version=self.trapi_version,
                        biolink_version=self.biolink_version,
                        )
                self.constraints.append(
                        _constraint.load(constraint_info, name=name)
                        )
        elif self.trapi_version == '1.1':
            self.ids = node_info.pop("ids", None)
            categories = node_info.pop("categories", None)
            if categories is not None:
                self.categories = [BiolinkEntity(category) for category in categories]
            constraints = node_info.pop("constraints", None)
            if constraints is not None:
                # Process constraints
                for constraint_info in constraints:
                    _constraint = QConstraintOrAdditionalProperty(
                            trapi_version=self.trapi_version,
                            biolink_version=self.biolink_version,
                            )
                    self.constraints.append(
                            _constraint.load(constraint_info)
                            )
        valid, message = self.validate()
        if valid:
            return self
        else:
            raise InvalidTrapiComponent(self.trapi_version, 'QNode', message)

    def add_constraint(self, 
            name,
            c_id,
            operator,
            value,
            unit_id=None,
            unit_name=None,
            c_not=False,
            edge_id=None,
            node_id=None,
            ):
        if self.constraints is None:
            self.constraints = []
        self.constraints.append(
                QConstraintOrAdditionalProperty(
                    self.trapi_version,
                    self.biolink_version,
                    name=name,
                    c_id=c_id,
                    operator=operator,
                    value=value,
                    unit_id=unit_id,
                    unit_name=unit_name,
                    c_not=c_not,
                    )
                )
        valid, message = self.validate()
        if not valid:
            raise InvalidTrapiComponent(trapi_version, 'QNode', message)

    def validate(self):
        _dict = self.to_dict()
        try:
            if self.trapi_version == '1.0':
                validate_QNode_1_0(_dict)
            elif self.trapi_version == '1.1':
                validate_QNode_1_1(_dict)
            else:
                raise UnsupportedTrapiVersion(self.trapi_version)
            return True, None 
        except ValidationError as ex:
                return False, ex.message

class QEdge(TrapiBaseClass):
    def __init__(self,
            trapi_version,
            biolink_version,
            q_subject='',
            q_object='',
            predicates=None,
            relation=None,
            constraints=[],
            ):
        self.subject = q_subject
        self.object = q_object
        self.predicates = predicates
        self.relation = relation
        self.constraints = constraints
        super().__init__(trapi_version, biolink_version)
        
        valid, message = self.validate()
        if not valid:
            raise InvalidTrapiComponent(trapi_version, 'QEdge', message)

    def to_dict(self):
        if self.trapi_version == '1.0':
            predicate = self.predicates
            if type(predicate) is not list and predicate is not None:
                predicate = predicate.get_curie()
            elif type(predicate) is list:
                predicate = [_predicate.get_curie() for _predicate in predicate]
            _dict = {
                    "predicate": predicate,
                    "relation": self.relation,
                    "subject": self.subject,
                    "object": self.object,
                    }
            if self.constraints is not None:
                for constraint in self.constraints:
                    _dict.update(constraint.to_dict())
            return _dict
        elif self.trapi_version == '1.1':
            predicates = self.predicates
            if type(predicates) is not list and predicates is not None:
                predicates = [predicates.get_curie()]
            elif type(predicates) is list:
                predicates = [predicate.get_curie() for predicate in predicates]
            _dict = {
                    "predicates": predicates,
                    "relation": self.relation,
                    "subject": self.subject,
                    "object": self.object,
                    }
            if self.constraints is not None:
                _dict["constraints"] = []
                for constraint in self.constraints:
                    _dict["constraints"].append(constraint.to_dict())
            return _dict
    
    def load(self, edge_info):
        if self.trapi_version == '1.0':
            self.subject = edge_info.pop("subject")
            self.object = edge_info.pop("object")
            predicates = edge_info.pop("predicate", None)
            if predicates is not None:
                if type(predicates) is list:
                    self.predicates = [BiolinkEntity(predicate) for predicate in predicates]
                else:
                    self.predicates = BiolinkEntity(predicates)
            self.relation = edge_info.pop("relation", None)
            # Process constraints
            for name, constraint_info in edge_info.items():
                _constraint = QConstraintOrAdditionalProperty(
                        trapi_version=self.trapi_version,
                        biolink_version=self.biolink_version,
                        )
                self.constraints.append(
                        _constraint.load(constraint_info, name=name)
                        )
        elif self.trapi_version == '1.1':
            self.subject = edge_info.pop("subject")
            self.object = edge_info.pop("object")
            predicates = edge_info.pop("predicates", None)
            if predicates is not None:
                self.predicates = [BiolinkEntity(predicate) for predicate in predicates]
            self.relation = edge_info.pop("relation", None)
            constraints = edge_info.pop("constraints", None)
            if constraints is not None:
                # Process constraints
                for constraint_info in constraints:
                    _constraint = QConstraintOrAdditionalProperty(
                            trapi_version=self.trapi_version,
                            biolink_version=self.biolink_version,
                            )
                    self.constraints.append(
                            _constraint.load(constraint_info)
                            )
        valid, message = self.validate()
        if valid:
            return self
        else:
            raise InvalidTrapiComponent(self.trapi_version, 'QEdge', message)
    
    def add_constraint(self, 
            name,
            c_id,
            operator,
            value,
            unit_id=None,
            unit_name=None,
            c_not=False,
            edge_id=None,
            node_id=None,
            ):
        if self.constraints is None:
            self.constraints = []
        self.constraints.append(
                QConstraintOrAdditionalProperty(
                    self.trapi_version,
                    self.biolink_version,
                    name=name,
                    c_id=c_id,
                    operator=operator,
                    value=value,
                    unit_id=unit_id,
                    unit_name=unit_name,
                    c_not=c_not,
                    )
                )
        valid, message = self.validate()
        if not valid:
            raise InvalidTrapiComponent(self.trapi_version, 'QEdge', message)
        
    def validate(self):
        _dict = self.to_dict()
        try:
            if self.trapi_version == '1.0':
                validate_QEdge_1_0(_dict)
            elif self.trapi_version == '1.1':
                validate_QEdge_1_1(_dict)
            else:
                raise UnsuppoertedTrapiVersion(self.trapi_version)
            return True, None 
        except ValidationError as ex:
                return False, ex.message

class QueryGraph(TrapiBaseClass):
    def __init__(self, trapi_version='1.1', biolink_version=None):
        self.nodes = {}
        self.edges = {}
        self.node_counter = 0
        self.edge_counter = 0
        super().__init__(trapi_version, biolink_version)

    def add_node(self, ids, categories):
        # Run categories through Biolink
        if categories is not list and categories is not None:
            categories = BiolinkEntity(categories, self.biolink_version)
        elif categories is not None:
            categories = [BiolinkEntity(category) for category in categories]
        node_id = 'n{}'.format(self.node_counter)
        self.node_counter += 1
        self.nodes[node_id] = QNode(
                self.trapi_version,
                self.biolink_version,
                ids=ids,
                categories=categories
                )
        return node_id

    def add_edge(self, q_subject, q_object, predicates, relation=None):
        # Run predicates through Biolink
        if predicates is not list and predicates is not None:
            predicates = BiolinkEntity(predicates, self.biolink_version)
        elif predicates is not None:
            predicates = [BiolinkEntity(predicate) for predicate in predicates]
        edge_id = 'e{}'.format(self.edge_counter)
        self.edge_counter += 1
        self.edges[edge_id] = QEdge(
                self.trapi_version,
                self.biolink_version,
                q_subject=q_subject,
                q_object=q_object,
                predicates=predicates,
                relation=relation,
                )
        return edge_id

    def add_constraint(self,
            name,
            c_id,
            operator,
            value,
            unit_id=None,
            unit_name=None,
            c_not=False,
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
        q_obj.add_constraint(
                name=name,
                c_id=c_id,
                operator=operator,
                value=value,
                unit_id=unit_id,
                unit_name=unit_name,
                c_not=c_not,
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
        if type(categories) == str:
            categories = [BiolinkEntity(categories)]
        elif type(categories) == list:
            categories = [BiolinkEntity(category) for category in categories]
        for node_id, node_info in self.nodes.items():
            if node_info.categories is not None:
                if type(node_info.categories) == BiolinkEntity:
                    node_categories = [node_info.categories]
                elif type(node_info.categories) == list:
                    node_categories = [category for category in node_info.categories]
            if categories is not None:
                if len(set(categories) - set(node_categories)) == 0:
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
                validate_QueryGraph_1_0(_dict)
            elif self.trapi_version == '1.1':
                validate_QueryGraph_1_1(_dict)
            else:
                raise UnsuppoertedTrapiVersion(self.trapi_version)
            return True, None 
        except ValidationError as ex:
            return False, ex.message

    def load(self, query_graph):
        # Load Nodes
        for node_id, node_info in query_graph["nodes"].items():
            _node = QNode(trapi_version=self.trapi_version, biolink_version=self.biolink_version)
            self.nodes[node_id] = _node.load(node_info)
        # Load Edges
        for edge_id, edge_info in query_graph["edges"].items():
            _edge = QEdge(trapi_version=self.trapi_version, biolink_version=self.biolink_version)
            self.edges[edge_id] = _edge.load(edge_info)
        valid, message = self.validate()
        if valid:
            return self
        else:
            raise InvalidTrapiComponent(self.trapi_version, 'QueryGraph', message)



