"""
TRAPI Query Graph Data Classes
"""
from jsonschema import ValidationError
from trapi_model import exceptions

from trapi_model.biolink.constants import get_biolink_entity
from trapi_model.biolink import BiolinkEntity
from trapi_model.exceptions import *
from trapi_model.base import TrapiBaseClass
from requests import request
from reasoner_validator import validate_QEdge_1_0, validate_QEdge_1_1, \
validate_QNode_1_0, validate_QNode_1_1, validate_QueryGraph_1_0, validate_QueryGraph_1_1

from processing_and_validation.meta_kg_validator import MetaKGValidator
from processing_and_validation.semantic_processor import SemanticProcessor
import logging
# Setup logging
logging.addLevelName(25, "NOTE")
# Add a special logging function
def note(self, message, *args, **kwargs):
    self._log(25, message, args, kwargs)
logging.Logger.note = note
logger = logging.getLogger(__name__)

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

    @staticmethod
    def load(trapi_version, biolink_version, constraint_info, name=None):
        if trapi_version == '1.0':
            constraint = QConstraintOrAdditionalProperty(
                    trapi_version,
                    biolink_version,
                    name=name,
                    c_id=constraint_info.pop("id"),
                    operator=constraint_info.pop("operator"),
                    value=constraint_info.pop("value"),
                    unit_id=constraint_info.pop("unit_id", None),
                    unit_name=constraint_info.pop("unit_name", None),
                    )
        elif trapi_version == '1.1':
            constraint = QConstraintOrAdditionalProperty(
                    trapi_version,
                    biolink_version,
                    name=constraint_info.pop("name"),
                    c_id=constraint_info.pop("id"),
                    operator= constraint_info.pop("operator"),
                    value=constraint_info.pop("value"),
                    unit_id=constraint_info.pop("unit_id", None),
                    unit_name=constraint_info.pop("unit_name", None),
                    c_not=constraint_info.pop("not", False),
                    )
        return constraint

class QNode(TrapiBaseClass):
    def __init__(self,
            trapi_version,
            biolink_version,
            ids = None,
            categories = None,
            constraints = None,
            ):
        if type(ids) is not list and ids is not None:
            ids = [ids]
        if type(categories) is not list and categories is not None:
            categories = [categories]
        self.ids = ids
        if constraints is None:
            self.constraints = []
        else:
            self.constraints = constraints
        self.categories = categories
        super().__init__(trapi_version, biolink_version)
        valid, message = self.validate()
        if not valid:
            raise InvalidTrapiComponent(trapi_version, 'QNode', message)

    def set_ids(self, ids):
        if type(ids) == str:
            self.ids = [ids]
        else:
            self.ids = ids
    
    def find_constraint(self, name):
        for constraint in self.constraints:
            if constraint.name == name:
                return constraint
        return None

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

    def to_dict(self): 
        # Get categories curies
        categories = self.categories
        if categories is not None:
            categories = [category.get_curie() for category in categories]
        if self.trapi_version == '1.0':
            _dict = {
                        "id": self.ids,
                        "category": categories,
                    }
            if self.constraints is not None:
                for constraint in self.constraints:
                    _dict.update(constraint.to_dict())
            return _dict
        elif self.trapi_version == '1.1':
            _dict = {
                        "ids": self.ids,
                        "categories": categories,
                        "constraints": []
                    }
            if self.constraints is not None:
                for constraint in self.constraints:
                    _dict["constraints"].append(constraint.to_dict())
            return _dict
        else:
            raise UnsupportedTrapiVersion(self.trapi_version)

    @staticmethod
    def load(trapi_version, biolink_version, node_info):
        if trapi_version == '1.0':
            qnode = QNode(trapi_version, biolink_version)
            ids = node_info.pop("id", None)
            if ids is not None:
                qnode.set_ids(ids)
            categories = node_info.pop("category", None)
            if categories is not None:
                qnode.set_categories(categories)
            # Process constraints
            for name, constraint_info in node_info.items():
                qnode.constraints.append(
                        QConstraintOrAdditionalProperty.load(
                            trapi_version,
                            biolink_version,
                            constraint_info,
                            name=name,
                            )
                        )
        elif trapi_version == '1.1':
            qnode = QNode(trapi_version, biolink_version)
            ids = node_info.pop("ids", None)
            if ids is not None:
                qnode.set_ids(ids)
            categories = node_info.pop("categories", None)
            if categories is not None:
                qnode.set_categories(categories)
            constraints = node_info.pop("constraints", None)
            if constraints is not None:
                # Process constraints
                for constraint_info in constraints:
                    qnode.constraints.append(
                            QConstraintOrAdditionalProperty.load(
                                trapi_version,
                                biolink_version,
                                constraint_info,
                                )
                            )
        valid, message = qnode.validate()
        if valid:
            return qnode
        else:
            raise InvalidTrapiComponent(trapi_version, 'QNode', message)

    def add_constraint(self, 
            name,
            c_id,
            operator,
            value,
            unit_id=None,
            unit_name=None,
            c_not=False,
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
            constraints=None,
            ):
        self.subject = q_subject
        self.object = q_object
        if type(predicates) is not list and predicates is not None:
            predicates = [predicates]
        self.predicates = predicates
        self.relation = relation
        if constraints is None:
            self.constraints = []
        else:
            self.constraints = constraints
        super().__init__(trapi_version, biolink_version)
        
        valid, message = self.validate()
        if not valid:
            raise InvalidTrapiComponent(trapi_version, 'QEdge', message)
        

    def find_constraint(self, name):
        for constraint in self.constraints:
            if constraint.name == name:
                return constraint
        return None
    
    def set_predicates(self, predicates):
        if type(predicates) is str:
            self.predicates = [get_biolink_entity(predicates)]
        elif type(predicates) is BiolinkEntity:
            self.predicates = [predicates]
        else:
            _predicates = []
            for predicate in predicates:
                if type(predicate) is str:
                    _predicates.append(get_biolink_entity(predicate))
                elif type(category) is BiolinkEntity:
                    _predicates.append(predicate)
            self.predicates = _predicates

    def to_dict(self):
        predicates = self.predicates
        if predicates is not None:
            predicates = [_predicate.get_curie() for _predicate in predicates]
        if self.trapi_version == '1.0':
            _dict = {
                    "predicate": predicates,
                    "relation": self.relation,
                    "subject": self.subject,
                    "object": self.object,
                    }
            if self.constraints is not None:
                for constraint in self.constraints:
                    _dict.update(constraint.to_dict())
            return _dict
        elif self.trapi_version == '1.1':
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
    
    @staticmethod
    def load(trapi_version, biolink_version, edge_info):
        qedge = QEdge(trapi_version, biolink_version)
        if trapi_version == '1.0':
            qedge.subject = edge_info.pop("subject")
            qedge.object = edge_info.pop("object")
            predicates = edge_info.pop("predicate", None)
            if predicates is not None:
                qedge.set_predicates(predicates)
            qedge.relation = edge_info.pop("relation", None)
            # Process constraints
            for name, constraint_info in edge_info.items():
                qedge.constraints.append(
                        QConstraintOrAdditionalProperty.load(
                            trapi_version,
                            biolink_version,
                            constraint_info,
                            name=name,
                            )
                        )
        elif trapi_version == '1.1':
            qedge.subject = edge_info.pop("subject")
            qedge.object = edge_info.pop("object")
            predicates = edge_info.pop("predicates", None)
            

            if predicates is not None:
                qedge.set_predicates(predicates)
            qedge.relation = edge_info.pop("relation", None)
            constraints = edge_info.pop("constraints", None)
            if constraints is not None:
                # Process constraints
                for constraint_info in constraints:
                    qedge.constraints.append(
                            QConstraintOrAdditionalProperty.load(
                                trapi_version,
                                biolink_version,
                                constraint_info,
                                )
                            )
        valid, message = qedge.validate()
        if valid:
            return qedge
        else:
            raise InvalidTrapiComponent(trapi_version, 'QEdge', message)
    
    def add_constraint(self, 
            name,
            c_id,
            operator,
            value,
            unit_id=None,
            unit_name=None,
            c_not=False,
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
                raise UnsupportedTrapiVersion(self.trapi_version)
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
        if type(categories) is not list and categories is not None:
            categories = [BiolinkEntity(categories, self.biolink_version)]
        elif categories is not None:
            categories = [BiolinkEntity(category, biolink_version=self.biolink_version) for category in categories]
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
        if type(predicates) is not list and predicates is not None:
            predicates = [BiolinkEntity(predicates, self.biolink_version)]
        elif predicates is not None:
            predicates = [BiolinkEntity(predicate, biolink_version=self.biolink_version) for predicate in predicates]
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

    @staticmethod
    def _is_categories_match(categories1, categories2):
        try:
            if categories1 == categories2:
                return True
        except:
            pass
        if categories1 is None or categories2 is None:
            return False
        # Try to reformat categories
        if type(categories1) is not list:
            categories1 = [categories1]
        if type(categories2) is not list:
            categories2 = [categories2]
        _categories1 = []
        for _category in categories1:
            if type(_category) is str:
                _categories1.append(get_biolink_entity(_category))
            elif type(_category) is BiolinkEntity:
                _categories1.append(_category)
            else:
                raise ValueError('Categories must be str or BiolinkEntities.')
        _categories2 = []
        for _category in categories2:
            if type(_category) is str:
                _categories2.append(get_biolink_entity(_category))
            elif type(_category) is BiolinkEntity:
                _categories2.append(_category)
            else:
                raise ValueError('Categories must be str or BiolinkEntities.')
        # Now test categories
        if len(set(_categories1) - set(_categories2)) == 0:
            return True
        return False
    
    @staticmethod
    def _is_ids_match(ids1, ids2):
        try:
            if categories1 == categories2:
                return True
        except:
            pass
        if ids1 is None or ids2 is None:
            return False
        if len(set(ids1) - set(ids2)) == 0:
            return True
        return False

    def find_nodes(self, categories=None, ids=None):
        matched_node_ids = []
        for node_id, node_info in self.nodes.items():
            if categories is not None:
                if not self._is_categories_match(categories, node_info.categories):
                    continue
            if ids is not None:
                if not self._is_ids_match(ids, node_info.ids):
                    continue
            matched_node_ids.append(node_id)
        if len(matched_node_ids) == 0:
            return None
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
    
    @staticmethod
    def load(trapi_version, biolink_version, query_graph, metakgValidation=True, semanticOperations=True):
        logger.note('loading query graph')
        new_query_graph = QueryGraph(trapi_version, biolink_version)
        # Load Nodes
        for node_id, node_info in query_graph["nodes"].items():
            new_query_graph.nodes[node_id] = QNode.load(trapi_version, biolink_version, node_info)
        # Load Edges
        for edge_id, edge_info in query_graph["edges"].items():
            new_query_graph.edges[edge_id] = QEdge.load(trapi_version, biolink_version, edge_info)
        if semanticOperations == True:
            try:
                logger.note('processing sub classes')
                sp = SemanticProcessor(new_query_graph)
                sp.process_biolink_subclasses()
                logger.note('processed')
            except:
                if metakgValidation == True :
                    mkgp = MetaKGValidator(new_query_graph)
                    mkgp.validate_graph()
        if metakgValidation == True:        
            logger.note('validating with meta kg')
            mkgp = MetaKGValidator(new_query_graph)
            mkgp.validate_graph()
            logger.note('validated')
        
        valid, message = new_query_graph.validate()
        if valid:
            logger.note('loading query graph')
            return new_query_graph
        else:
            raise InvalidTrapiComponent(trapi_version, 'QueryGraph', message)