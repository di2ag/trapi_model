import requests
import json
from trapi_model.query_graph import QueryGraph
from trapi_model.biolink.constants import get_biolink_entity
from processing_and_validation.semantic_processor_exceptions import IndeterminableWildcardDescendent, UnsupportedCategoryAncestors, UnsupportedPredicateAncestor
import yaml

class SemanticProcessor():
    
    def __init__(self) -> None:
        self._get_meta_kg()
        self._get_node_definitions()
        self._get_edge_definitions()
        self._get_wildcard_definitions()

    def _biolink_category_descendent_lookup(self, biolinkCategory) -> json:
            url = "https://bl-lookup-sri.renci.org/bl/"+biolinkCategory+"/descendants?version=latest"
            response = requests.get(url)

            return response.json()
        
    def _get_meta_kg(self)->None:
        meta_kg_file = open('schemas/meta-kg.json', 'r')
        self.meta_kg = json.load(meta_kg_file)
    
    def _get_wildcard_definitions(self)->None:        
        metakg_edge_definitions = self.meta_kg["edges"]
        self.wildcard_definitions = {}

        for metakg_edge_definition in metakg_edge_definitions:
            subject_category = metakg_edge_definition["subject"]
            predicate = metakg_edge_definition["predicate"]
            object_category = metakg_edge_definition["object"]
            
            if self.wildcard_definitions.get(object_category) == None:
                self.wildcard_definitions.update({object_category : list()})

            self.wildcard_definitions[object_category].append({predicate:subject_category})
        
    
    def _get_node_definitions(self)->None:
        metakg_node_definitions = self.meta_kg["nodes"]
        self.supported_categories = metakg_node_definitions.keys()
        self._node_definitions = dict()
        for node_definition in metakg_node_definitions:
            for prefix in metakg_node_definitions[node_definition]["id_prefixes"]:
                self._node_definitions.update({prefix:node_definition})

    def _get_edge_definitions(self)->None:
        metakg_edge_definitions = self.meta_kg["edges"]
        self.edge_definitions = dict()
        for metakg_edge_definition in metakg_edge_definitions:
            subject = metakg_edge_definition["subject"]
            predicate = metakg_edge_definition["predicate"]
            object = metakg_edge_definition["object"]
            if self.edge_definitions.get(subject) == None:
                self.edge_definitions.update({subject:({object:predicate})})
            else:
                tmp_dict = self.edge_definitions.get(subject)
                tmp_dict.update({object:predicate})
                self.edge_definitions.update({subject:tmp_dict})

    def _process_nodes(self, query_graph: QueryGraph) -> None:
        qnodes = query_graph.nodes
        for qnode in qnodes:
            node_obj = qnodes[qnode]
            curies = node_obj.ids
            if curies is not None:
                for curie in curies:
                    #check if we support the specificied categories
                    #if we do not support the specified categories, see if we can support descendants
                    curie = curie[:curie.index(':')]
                    provided_categories = [category.passed_name for category in node_obj.categories]
                    expected_category = self._node_definitions.get(curie)
                    if expected_category not in provided_categories:
                        category_descendant_found = False
                        for provided_category in provided_categories:
                            descendants = self._biolink_category_descendent_lookup(provided_category)
                            if expected_category in descendants:
                                category_descendant_found = True
                                node_obj.set_categories(expected_category)
                                query_graph.nodes[qnode] = node_obj
                        if category_descendant_found == False:
                            raise UnsupportedCategoryAncestors(provided_categories)
                        qnodes[qnode] = node_obj
    
    def _process_edges(self, query_graph:QueryGraph):
        edges = query_graph.edges
        nodes = query_graph.nodes

        for edge in edges:
            edge_obj = edges[edge]
            provided_predicates = [predicate.passed_name for predicate in edge_obj.predicates]

            subject_node = nodes[edge_obj.subject]
            provided_subject_categories = [category.passed_name for category in subject_node.categories]
            
            object_node = nodes[edge_obj.object]
            provided_object_categories = [category.passed_name for category in object_node.categories]
            
            if subject_node.ids is not None: 
                for subject_category in provided_subject_categories:
                    for object_category in provided_object_categories:
                        
                        expected_predicate = self.edge_definitions.get(subject_category).get(object_category)
                        if expected_predicate not in provided_predicates:
                            for provided_predicate in provided_predicates:
                                descendants = self._biolink_category_descendent_lookup(provided_predicate)
                                if expected_predicate in descendants:
                                    edge_obj.set_predicates(expected_predicate)
                                    query_graph.edges[edge] = edge_obj
                                else:
                                    raise UnsupportedPredicateAncestor(provided_predicates)

    def _process_subject_wildcard(self, query_graph, wildcard_node, wildcard_edge):
        matches_found = 0
        tuple_match = ()
        
        nodes = query_graph.nodes
        edges = query_graph.edges

        object_node = [edges[wildcard_edge].object][0]

        wildcard_object_categories = [category.passed_name for category in nodes[object_node].categories]
        provided_predicates = [predicate.passed_name for predicate in edges[wildcard_edge].predicates]
        provided_subject_categories = [category.passed_name for category in nodes[wildcard_node].categories]
    
        for wildcard_object_category in wildcard_object_categories:
            possible_subject_predicate_tuples = self.wildcard_definitions.get(wildcard_object_category)
            for i, possible_subject_predicate_tuple in enumerate(possible_subject_predicate_tuples, 1):
                
                possible_predicate = list(possible_subject_predicate_tuple.keys())[0]
                possible_subject = possible_subject_predicate_tuple[possible_predicate]
                
                for provided_subject_category in provided_subject_categories:
                    for provided_predicate in provided_predicates:
                        wildcard_subject_descendents = self._biolink_category_descendent_lookup(provided_subject_category)
                        wildcard_subject_descendents.append(provided_subject_category)

                        provided_predicate_descendents = self._biolink_category_descendent_lookup(provided_predicate)
                        provided_predicate_descendents.append(provided_predicate)

                        wildcard_subject_descendents = set(wildcard_subject_descendents)
                        if possible_predicate in provided_predicate_descendents and possible_subject in wildcard_subject_descendents:
                            matches_found = matches_found + 1
                            tuple_match = (possible_subject,possible_predicate)
                        elif i == len(possible_subject_predicate_tuples) and matches_found != 1:
                            if possible_predicate not in provided_predicate_descendents:
                                raise UnsupportedPredicateAncestor(provided_predicate)
                            else:
                                raise UnsupportedCategoryAncestors(provided_subject_category)
        
        wildcard_node_obj = nodes[wildcard_node]   
        if matches_found == 1:            
            wildcard_node_obj.set_categories(tuple_match[0])
            wildcard_edge_obj = edges[wildcard_edge]
            wildcard_edge_obj.set_predicates(tuple_match[1])
        else:
            raise IndeterminableWildcardDescendent(wildcard_node_obj.categories)
                        

    def _process_object_wildcard(self, query_graph, wildcard_node, wildcard_edge):
        matches_found = 0
        tuple_match = ()
        
        nodes = query_graph.nodes
        edges = query_graph.edges

        subject_node = [edges[wildcard_edge].subject][0]

        provided_object_categories = [category.passed_name for category in nodes[subject_node].categories]
        provided_predicates = [predicate.passed_name for predicate in edges[wildcard_edge].predicates]
        wildcard_object_categories = [category.passed_name for category in nodes[wildcard_node].categories]
    
        for wildcard_subject_category in wildcard_object_categories:
            possible_object_predicate_tuples = self.wildcard_definitions.get(wildcard_subject_category)
            for i, possible_object_predicate_tuple in enumerate(possible_object_predicate_tuples, 1):
                
                possible_predicate = list(possible_object_predicate_tuple.keys())[0]
                possible_object = possible_object_predicate_tuple[possible_predicate]
                
                for provided_object_category in provided_object_categories:
                    for provided_predicate in provided_predicates:
                        wildcard_object_descendents = self._biolink_category_descendent_lookup(provided_object_category)

                        provided_predicate_descendents = self._biolink_category_descendent_lookup(provided_predicate)

                        wildcard_object_descendents = set(wildcard_object_descendents)
                        
                        if possible_predicate in provided_predicate_descendents and possible_object in wildcard_object_descendents:
                            matches_found = matches_found + 1
                            tuple_match = (possible_object,possible_predicate)
                        elif i == len(possible_object_predicate_tuples)  and matches_found != 1:
                            if possible_predicate not in provided_predicate_descendents:
                                raise UnsupportedPredicateAncestor(provided_predicate)
                            else:
                                raise UnsupportedCategoryAncestors(provided_object_category)
        
        wildcard_node_obj = nodes[wildcard_node]   
        if matches_found == 1:            
            wildcard_node_obj.set_categories(tuple_match[0])
            wildcard_edge_obj = edges[wildcard_edge]
            wildcard_edge_obj.set_predicates(tuple_match[1])
        else:
            raise IndeterminableWildcardDescendent(wildcard_node_obj.categories)

    def _identify_wildcard(self, query_graph:QueryGraph):
        nodes = query_graph.nodes
        edges = query_graph.edges

        for node in nodes:
            if nodes[node].ids == None:
                for edge in edges:
                    if node == edges[edge].subject:
                        return (node,edge,"subject")
                    elif node == edges[edge].object:
                        return (node,edge,"object")
        return None

    def _is_wildcard(self, query_graph:QueryGraph):
        
        nodes = query_graph.nodes
        
        for node in nodes:
            if nodes[node].ids == None:
                return True
        
        return False

    def process(self, query_graph: QueryGraph)-> QueryGraph:
        self._process_nodes(query_graph)
        self._process_edges(query_graph)

        if self._is_wildcard(query_graph):
            wildcard_node,wildcard_edge,wildcard_type = self._identify_wildcard(query_graph)
            if wildcard_node is not None:
                if wildcard_type == "subject":
                    self._process_subject_wildcard(query_graph, wildcard_node, wildcard_edge)
                elif wildcard_type == "object":
                    self._process_object_wildcard(query_graph, wildcard_node, wildcard_edge)
        return query_graph
