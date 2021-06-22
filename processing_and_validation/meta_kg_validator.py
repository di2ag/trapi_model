import requests
from processing_and_validation.metakg_validation_exceptions import *
import logging
import json
# Setup logging
logging.addLevelName(25, "NOTE")
# Add a special logging function
def note(self, message, *args, **kwargs):
    self._log(25, message, args, kwargs)
logging.Logger.note = note
logger = logging.getLogger(__name__)

class MetaKGValidator:
    def __init__(self, query_graph) -> None:
        self.meta_knowledge_graph_location = "http://chp.thayer.dartmouth.edu/meta_knowledge_graph/"
        self._get_meta_knowledge_graph()
        self._get_supported_categories()
        self._get_supported_predicates()
        self._get_supported_id_prefixes()
        self._get_supported_relationships()
        self._get_suppported_prefix_category_pairs()
        self.query_graph = query_graph

    def _get_meta_knowledge_graph(self) -> None:
        response = requests.get(self.meta_knowledge_graph_location)
        meta_knowledge_graph = response.json()
        self.meta_knowledge_graph = meta_knowledge_graph
    
    def _get_supported_categories(self) -> None:
        self.supported_categories = set()
        for edge in self.meta_knowledge_graph['edges']:
            supported_subject = edge['subject']
            supported_object = edge['object']
            self.supported_categories.add(supported_subject)
            self.supported_categories.add(supported_object)

    def _get_supported_predicates(self) -> None:
        self.supported_predicates = set()
        for edge in self.meta_knowledge_graph['edges']:
            supported_predicate = edge['predicate']
            self.supported_predicates.add(supported_predicate)
        self.supported_predicates = list(self.supported_predicates)

    def _get_supported_id_prefixes(self) -> None:
        self.supported_id_prefixes = set()
        nodes = self.meta_knowledge_graph['nodes']
        for node_category in nodes:
            for id_prefix in nodes[node_category]['id_prefixes']:
                self.supported_id_prefixes.add(id_prefix)
        
    
    def _get_suppported_prefix_category_pairs(self) -> None:
        self.supported_prefix_category_pairs = dict()
        nodeCategories = self.meta_knowledge_graph['nodes'].keys()
        for node_category in nodeCategories:
            id_prefixes = self.meta_knowledge_graph['nodes'][node_category]['id_prefixes']
            self.supported_prefix_category_pairs.update({node_category:id_prefixes})          

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
        if ids is not None:
            for id in ids:
                prefix = id[:id.index(':')]
                if prefix not in self.supported_id_prefixes:
                    validated = False
        
        if validated:
            return True
        else:
            raise UnsupportedPrefix(prefix)

    def _validate_prefix_category_pairs(self, ids:list, categories:list) -> bool:
        validated = True
        if ids is not None:
            prefix = ""
            passed_name = ""
            for id in ids:
                prefix = id[:id.index(':')]
                passed_names = [category.passed_name for category in categories]
                for passed_name in passed_names:
                    if prefix not in self.supported_prefix_category_pairs.get(passed_name):
                        validated = False
        if validated:
            return True
        else:
            raise UnsupportedPrefixCategoryPair(entity=passed_name, prefix=prefix)

    def _validate_predicates(self, predicates:list) -> bool:
        validated = False
        passed_names = [predicate.passed_name for predicate in predicates]
        for passed_name in passed_names:
            if passed_name in self.supported_predicates:
                validated = True
        
        if validated:
            return True
        else:
            raise UnsupportedPredicate(passed_names)

    def _validate_categories(self, categories:list) -> bool:
        validated = False
        passed_names = [category.passed_name for category in categories]
        for passed_name in passed_names:
            if passed_name in self.supported_categories:
                validated = True
            else:
                raise UnsupportedCategory(passed_name)
        if validated:
            return True
        else:
            raise UnsupportedCategory(passed_name)
    
    def _validate_relationship(self, subjects: str, predicates: list, objects:str) -> bool:
        validated = True
        for subject in subjects:
            for predicate in predicates:
                for object in objects:
                    relationship = (subject.passed_name, predicate.passed_name, object.passed_name)
                    if relationship not in self.supported_relationships:
                        validated = False 

        if validated:
            return True
        else:
            raise UnsupportedNodeEdgeRelationship(subject.passed_name, predicate.passed_name, object.passed_name)

    def _validate_nodes(self, nodes:list):
        for node in nodes:
            ids = nodes[node].ids
            self._validate_prefixes(ids)

            categories = nodes[node].categories
            self._validate_categories(categories)
            self._validate_prefix_category_pairs(ids,categories)

    def _validate_edges(self, edges:list, nodes:list):
        for edge in edges:
            predicates = edges[edge].predicates
            self._validate_predicates(predicates)
            

    def validate_graph(self) -> None:
        #get nodes
        nodes = self.query_graph.nodes
        self._validate_nodes(nodes)
        #get edges
        edges = self.query_graph.edges
        self._validate_edges(edges,nodes)

        for edge in edges:
            subjects = nodes.get(edges[edge].subject).categories
            objects = nodes.get(edges[edge].object).categories
            self._validate_relationship(subjects,edges[edge].predicates,objects)
