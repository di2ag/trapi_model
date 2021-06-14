from sys import prefix
import requests
from trapi_model.exceptions import UnsupportedNodeEdgeRelationship, UnsupportedPrefixEntityPair, UnsupportedPredicate, UnsupportedEntity, UnsupportedPrefix

class MetaKGValidator:
    def __init__(self) -> None:
        self.meta_knowledge_graph_location = "http://chp.thayer.dartmouth.edu/mmeta_knowledge_graph/"
        self._get_meta_knowledge_graph()
        self._get_supported_entities()
        self._get_supported_predicates()
        self._get_supported_id_prefixes()
        self._get_supported_relationships()
        self._get_suppported_prefix_entitiy_pairs()
        
    def _get_meta_knowledge_graph(self) -> None:
        response = requests.get(self.meta_knowledge_graph_location)
        meta_knowledge_graph = response.data
        self.meta_knowledge_graph = meta_knowledge_graph
    
    def _get_supported_entities(self) -> None:
        self.supported_entities = set()
        for edge in self.meta_knowledge_graph['edges']:
            supported_subject = edge['subject']
            supported_object = edge['object']
            self.supported_entities.add(supported_subject)
            self.supported_entities.add(supported_object)

    def _get_supported_predicates(self) -> None:
        self.supported_predicates = set()
        for edge in self.meta_knowledge_graph:
            supported_predicate = edge['predicate']
            self.supported_predicates.add(supported_predicate)

    def _get_supported_id_prefixes(self) -> None:
        self.supported_id_prefixes = set()
        for node_entity in self.meta_knowledge_graph['nodes']:
            for id_prefix in node_entity['id_prefixes']:
                self.supported_id_prefixes.add(id_prefix)
    
    def _get_suppported_prefix_entitiy_pairs(self) -> None:
        self.supported_prefix_entity_pairs = dict()
        nodeEntities = self.meta_knowledge_graph['nodes'].keys()
        for nodeEntity in nodeEntities:
            id_prefixes = self.meta_knowledge_graph[nodeEntity]['id_prefixes']
            self.supported_predicates.update({nodeEntity:id_prefixes})          

    def _get_supported_relationships(self) -> None:
        self.supported_relationships = set()
        for edge_relationship in self.meta_knowledge_graph['edges']:
            
            subject = edge_relationship['subject']
            predicate = edge_relationship['predicate']
            object = edge_relationship['object']

            relationship = (subject, predicate, object)
            self.supported_relationships.add(relationship)

    def _validate_prefixes(self, ids:list) -> bool:
        validated = True
        for id in ids:
            prefix = id[:':'-1]
            if prefix not in self.supported_id_prefixes:
                validated = False
        
        if validated:
            return True
        else:
            raise UnsupportedPrefix(prefix)

    def _validate_prefix_entity_pairs(self, ids:list, categories:list) -> bool:
        validated = True
        for id in ids:
            prefix = id[:':'-1]
            for category in categories:
                if prefix not in self.supported_prefix_entity_pairs.get(category):
                    validated = False
        if validated:
            return True
        else:
            raise UnsupportedPrefixEntityPair

    def _validate_predicate(self, predicates:list) -> bool:
        validated = True

        for predicate in predicates:
            if predicate in self.supported_predicates:
                validated = False
        
        if validated:
            return True
        else:
            raise UnsupportedPredicate(predicate)

    def _validate_entities(self, entities:list) -> bool:
        validated = False
        unsupported_entity = None

        for entity in entities:
            if entity in self.supported_entities:
                validated = True
            else:
                unsupported_entity = entity
        if validated:
            return True
        else:
            raise UnsupportedEntity(unsupported_entity)
    
    def _validate_entity(self, entity:str) -> bool:
        validated = False
        if entity in self.supported_entities:
            validated = True

        if validated:
            return True
        else:
            raise UnsupportedEntity(entity)

    def _validate_relationship(self, subject: str, predicate: str, object:str) -> bool:
        validated = True
        relationship = (subject, predicate, object)
        if relationship not in self.supported_relationships:
            validated = False 

        if validated:
            return True
        else:
            raise UnsupportedNodeEdgeRelationship(subject, predicate, object)


