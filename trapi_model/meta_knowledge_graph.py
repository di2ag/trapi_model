import copy
import json
from collections import defaultdict
from jsonschema import ValidationError

from trapi_model.base import TrapiBaseClass
from trapi_model.biolink.constants import get_biolink_entity
from trapi_model.exceptions import *

from reasoner_validator import validate_MetaNode_1_1, validate_MetaEdge_1_1, validate_MetaKnowledgeGraph_1_1

class MetaNode(TrapiBaseClass):
    def __init__(self, id_prefixes, trapi_version, biolink_version):
        self.id_prefixes = id_prefixes
        super().__init__(trapi_version, biolink_version)
        valid, message = self.validate()
        if not valid:
            raise InvalidTrapiComponent(trapi_version, 'MetaNode', message)

    def add_prefix(self, prefix):
        self.id_prefixes.append(prefix)

    def to_dict(self):
        return {
                "id_prefixes": self.id_prefixes,
                }
    
    @staticmethod
    def load(meta_node_info, trapi_version, biolink_version):
        id_prefixes = meta_node_info.pop("id_prefixes")
        return MetaNode(
                id_prefixes,
                trapi_version,
                biolink_version,
                )
    
    def validate(self):
        _dict = self.to_dict()
        try:
            if self.trapi_version == '1.1':
                validate_MetaNode_1_1(_dict)
            else:
                raise UnsupportedTrapiVersion(self.trapi_version)
            return True, None 
        except ValidationError as ex:
                return False, ex.message

class MetaEdge(TrapiBaseClass):
    def __init__(self, q_subject, q_object, predicate, trapi_version, biolink_version):
        self.subject = q_subject
        self.object = q_object
        self.predicate = predicate
        if type(q_subject) is str:
            self.subject = get_biolink_entity(q_subject)
        if type(q_object) is str:
            self.object = get_biolink_entity(q_object)
        if type(predicate) is str:
            self.predicate = get_biolink_entity(predicate)
        super().__init__(trapi_version, biolink_version)
        valid, message = self.validate()
        if not valid:
            raise InvalidTrapiComponent(trapi_version, 'MetaEdge', message)

    def to_dict(self):
        return {
                "subject": self.subject.get_curie(),
                "object": self.object.get_curie(),
                "predicate": self.predicate.get_curie(),
                }

    @staticmethod
    def load(meta_edge_info, trapi_version, biolink_version):
        q_subject = meta_edge_info.pop("subject")
        q_object = meta_edge_info.pop("object")
        predicate = meta_edge_info.pop("predicate")
        return MetaEdge(
                q_subject,
                q_object,
                predicate,
                trapi_version,
                biolink_version,
                )

    def get_inverse(self):
        if self.predicate.get_inverse() is not None:
            return MetaEdge(
                    self.object,
                    self.subject,
                    self.predicate.get_inverse(),
                    self.trapi_version,
                    self.biolink_version,
                    )
        return None
    
    def validate(self):
        _dict = self.to_dict()
        try:
            if self.trapi_version == '1.1':
                validate_MetaEdge_1_1(_dict)
            else:
                raise UnsupportedTrapiVersion(self.trapi_version)
            return True, None 
        except ValidationError as ex:
                return False, ex.message

class MetaKnowledgeGraph(TrapiBaseClass):
    def __init__(self, trapi_version, biolink_version):
        self.nodes = {}
        self.edges = []
        super().__init__(trapi_version, biolink_version)

    def expand_with_inverses(self):
        # Try to expand all edges with there biolink inverses
        new_meta_kg = copy.deepcopy(self)
        for metaedge in self.edges:
            inverse_metaedge = metaedge.get_inverse()
            if inverse_metaedge is not None and inverse_metaedge not in new_meta_kg.edges:
                new_meta_kg.edges.append(inverse_metaedge)
        valid, message = new_meta_kg.validate()
        if not valid:
            raise InvalidTrapiComponent(self.trapi_version, 'MetaKnowledgeGraph', message)
        return new_meta_kg

    def to_dict(self):
        _dict = {'nodes': {}, 'edges':[]}
        for biolink_entity, metanode in self.nodes.items():
            _dict['nodes'][biolink_entity.get_curie()] = metanode.to_dict()
        for metaedge in self.edges:
            _dict['edges'].append(metaedge.to_dict())
        return _dict    

    def add_node(self, biolink_entity, id_prefixes):
        if type(id_prefixes) is str:
            id_prefixes = [id_prefixes]
        elif id_prefixes is not list:
            raise ValueError('Id prefixes must be a string or list.')
        if type(biolink_entity) is str:
            biolink_entity = get_biolink_entity(biolink_entity)
        self.nodes[biolink_entity] = MetaNode(id_prefixes, self.trapi_version, self.biolink_version)
        return biolink_entity

    def add_edge(
            self,
            q_subject,
            q_object, 
            predicate,
            ):
        if type(q_subject) is str:
            q_subject = get_biolink_entity(q_subject)
        if type(q_object) is str:
            q_object = get_biolink_entity(q_object)
        if type(predicate) is str:
            predicate = get_biolink_entity(predicate)
        self.edges.append(MetaEdge(
                    q_subject,
                    q_object,
                    predicate,
                    self.trapi_version,
                    self.biolink_version,
                    )
                )
    
    def validate(self):
        _dict = self.to_dict()
        try:
            if self.trapi_version == '1.1':
                validate_MetaKnowledgeGraph_1_1(_dict)
            else:
                raise UnsupportedTrapiVersion(self.trapi_version)
            return True, None 
        except ValidationError as ex:
                return False, ex.message

    @staticmethod
    def load(trapi_version, biolink_version, meta_knowledge_graph=None, filename=None):
        if filename is not None:
            with open(filename, 'r') as metakg_file:
                meta_knowledge_graph = json.load(metakg_file)
        new_meta_knowledge_graph = MetaKnowledgeGraph(trapi_version, biolink_version)
        # Load Nodes
        for biolink_curie, node_info in meta_knowledge_graph["nodes"].items():
            biolink_entity = get_biolink_entity(biolink_curie)
            new_meta_knowledge_graph.nodes[biolink_entity] = MetaNode.load(node_info, trapi_version, biolink_version)
        # Load Edges
        for edge_info in meta_knowledge_graph["edges"]:
            new_meta_knowledge_graph.edges.append(MetaEdge.load(edge_info, trapi_version, biolink_version))
        
        valid, message = new_meta_knowledge_graph.validate()
        if valid:
            return new_meta_knowledge_graph
        else:
            raise InvalidTrapiComponent(trapi_version, 'MetaKnowledgeGraph', message)
