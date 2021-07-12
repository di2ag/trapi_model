import requests
import json
from trapi_model import query_graph
from trapi_model.biolink.constants import get_biolink_entity
from trapi_model.processing_and_validation.semantic_processor_exceptions import *

class SemanticProcessor():
    
    def __init__(self, query_graph: query_graph) -> None:
        self.query_graph = query_graph

    def _biolink_category_descendent_lookup(self, biolinkCategory) -> json:
            url = "https://bl-lookup-sri.renci.org/bl/"+biolinkCategory+"/descendants?version=latest"
            response = requests.get(url)
            return response.json()
        
    def _process_nodes(self) -> list: 
        #get nodes
        nodes = self.query_graph.nodes
        
        #loop through nodes, check for appropriate biolink category given id
        for node in nodes:
            node_obj = nodes[node]
            curies = node_obj.ids
            if curies is not None:
                for curie in curies:
                    #check if we support the specificied categories
                    #if we do not support the specified categories, see if we can support descendants 
                    if "MONDO" in curie:
                        if get_biolink_entity("biolink:Disease") not in node_obj.categories:
                            category_ancestory_found = False
                            for category in node_obj.categories:
                                descendants = self._biolink_category_descendent_lookup(category.passed_name)
                                if "biolink:Disease" in descendants:
                                    category_ancestory_found = True
                                    node_obj.set_categories("biolink:Disease")
                            if category_ancestory_found == False:
                                passed_names = [category.passed_name for category in node_obj.categories]
                    elif "ENSEMBL" in curie:
                        self.gene_nodes_found = True
                        if get_biolink_entity("biolink:Gene") not in node_obj.categories:
                            category_ancestory_found = False
                            for category in node_obj.categories:
                                descendants = self._biolink_category_descendent_lookup(category.passed_name)
                                if "biolink:Gene" in descendants:
                                    category_ancestory_found = True
                                    node_obj.set_categories("biolink:Gene")
                            if category_ancestory_found == False:
                                passed_names = [category.passed_name for category in node_obj.categories]
                                raise UnsupportedCategoryAncestors(passed_names)
                    elif "CHEMBL" in curie:
                        self.drug_nodes_found = True
                        category_ancestory_found = False
                        if get_biolink_entity("biolink:Drug") not in node_obj.categories:
                            for category in node_obj.categories:
                                descendants = self._biolink_category_descendent_lookup(category.passed_name)
                                if "biolink:Drug" in descendants:
                                    category_ancestory_found = True
                                    node_obj.set_categories("biolink:Drug")
                            if category_ancestory_found == False:
                                passed_names = [category.passed_name for category in node_obj.categories]
                                raise UnsupportedCategoryAncestors(passed_names)
                    elif "EFO" in curie:
                        if get_biolink_entity("biolink:PhenotypicFeature") not in node_obj.categories:
                            category_ancestory_found = False
                            for category in node_obj.categories:
                                descendants = self._biolink_category_descendent_lookup(category.passed_name)
                                if "biolink:PhenotypicFeature" in descendants:
                                    category_ancestory_found = True
                                    node_obj.set_categories("biolink:PhenotypicFeature")
                            if category_ancestory_found == False:
                                passed_names = [category.passed_name for category in node_obj.categories]
                                raise UnsupportedCategoryAncestors(passed_names)
                self.query_graph.nodes[node] = node_obj
    
    def _process_edges(self) -> list:
        #get eges
        edges = self.query_graph.edges

        #get nodes
        nodes = self.query_graph.nodes

        #loop through edges, check for appropriate biolink predicate given subject and object categories
        for edge in edges:
            edge_obj = edges[edge]
            if nodes[edge_obj.subject].ids is not None and nodes[edge_obj.object].ids is not None:  
                for subject_id in nodes[edge_obj.subject].ids:
                    for object_id in nodes[edge_obj.object].ids:
                        if "ENSEMBL" in subject_id:
                            if "CHEMBL" in object_id:
                                if get_biolink_entity("biolink:interacts_with") not in edge_obj.predicates:
                                    predicate_ancestor_found = False
                                    for predicate in edge_obj.predicates:
                                        predicate_ancestor_found = True
                                        descendants = self._biolink_category_descendent_lookup(predicate.passed_name)
                                        if "biolink:interacts_with" in descendants:
                                            edge_obj.set_predicates("biolink:interacts_with")
                                    if predicate_ancestor_found == False:
                                        passed_names = [predicate.passed_name for predicate in edge_obj.predicates]
                                        raise UnsupportedPredicateAncestor(passed_names)
                            if "MONDO" in object_id:
                                if get_biolink_entity("biolink:gene_associated_with_condition") not in edge_obj.predicates:
                                    predicate_ancestor_found = False
                                    for predicate in edge_obj.predicates:
                                        descendants = self._biolink_category_descendent_lookup(predicate.passed_name)
                                        if "biolink:gene_associated_with_condition" in descendants:
                                            predicate_ancestor_found = True
                                            edge_obj.set_predicates("biolink:gene_associated_with_condition")
                                    if predicate_ancestor_found == False:
                                        passed_names = [predicate.passed_name for predicate in edge_obj.predicates]
                                        raise UnsupportedPredicateAncestor(passed_names)
                        if "CHEMBL" in subject_id:
                            if "MONDO" in object_id:
                                if get_biolink_entity("biolink:treats") not in edge_obj.predicates:
                                    predicate_ancestor_found = False
                                    for predicate in edge_obj.predicates:
                                        descendants = self._biolink_category_descendent_lookup(predicate.passed_name)
                                        if "biolink:treats" in descendants:
                                            predicate_ancestor_found = True
                                            edge_obj.set_predicates("biolink:treats")
                                    if predicate_ancestor_found == False:
                                        passed_names = [predicate.passed_name for predicate in edge_obj.predicates]
                                        raise UnsupportedPredicateAncestor(passed_names)
                            if "ENSEMBL" in object_id:
                                if get_biolink_entity("biolink:interacts_with") not in edge_obj.predicates:
                                    predicate_ancestor_found = False
                                    for predicate in edge_obj.predicates:
                                        descendants = self._biolink_category_descendent_lookup(predicate.passed_name)
                                        if "biolink:interacts_with" in descendants:
                                            predicate_ancestor_found = True
                                            edge_obj.set_predicates("biolink:interacts_with")
                                    if predicate_ancestor_found == False:
                                        passed_names = [predicate.passed_name for predicate in edge_obj.predicates]
                                        raise UnsupportedPredicateAncestor(passed_names)
                        if "MONDO" in subject_id:
                            if "EFO" in object_id:
                                if get_biolink_entity("biolink:has_phenotype") not in edge_obj.predicates:
                                    predicate_ancestor_found = False
                                    for predicate in edge_obj.predicates:
                                        descendants = self._biolink_category_descendent_lookup(predicate.passed_name)
                                        if "biolink:has_phenotype" in descendants:
                                            predicate_ancestor_found = True
                                            edge_obj.set_predicates("biolink:has_phenotype")
                                    if predicate_ancestor_found == False:
                                        passed_names = [predicate.passed_name for predicate in edge_obj.predicates]
                                        raise UnsupportedPredicateAncestor(passed_names)
                        self.query_graph.edges[edge] = edge_obj
    
    def _process_gene_wildcard_query(self):
        #get edges
        edges = self.query_graph.edges
        #get nodes
        nodes = self.query_graph.nodes

        for node in nodes:
            node_obj = nodes[node]
            if node_obj.ids is None:
                category_ancestor_found = False
                for category in node_obj.categories:
                    descendants = self._biolink_category_descendent_lookup(category.passed_name)
                    if "biolink:Gene" in descendants:
                        category_ancestor_found = True
                        node_obj.set_categories("biolink:Gene")
                        self.query_graph.nodes[node] = node_obj
                        for edge in edges:
                            edge_obj = edges[edge]
                            object_categories_passed_names = [category.passed_name for category in nodes[edge_obj.object].categories]
                            if edge_obj.subject == node and "biolink:Disease" in object_categories_passed_names:
                                predicate_descendent_found = False
                                for predicate in edge_obj.predicates:
                                    descendants = self._biolink_category_descendent_lookup(predicate.passed_name)
                                    if "biolink:gene_associated_with_condition" in descendants:
                                        predicate_descendent_found = True
                                        edge_obj.set_predicates("biolink:gene_associated_with_condition")
                                        self.query_graph.edges[edge] = edge_obj
                                        continue
                                if predicate_descendent_found == False:
                                    passed_names = [predicate.passed_name for predicate in edge_obj.predicates]
                                    raise UnsupportedPredicateAncestor(passed_names)
                            elif edge_obj.subject == node and "biolink:Drug" in object_categories_passed_names:
                                predicate_descendent_found = False
                                for predicate in edge_obj.predicates:
                                    descendants = self._biolink_category_descendent_lookup(predicate.passed_name)
                                    if "biolink:interacts_with" in descendants:
                                        predicate_descendent_found = True
                                        edge_obj.set_predicates("biolink:interacts_with")
                                        self.query_graph.edges[edge] = edge_obj
                                        continue
                                if predicate_descendent_found == False:
                                    passed_names = [predicate.passed_name for predicate in edge_obj.predicates]
                                    raise UnsupportedPredicateAncestor(passed_names)
                            elif edge_obj.subject == node and "biolink:Gene" in object_categories_passed_names:
                                predicate_descendent_found = False
                                for predicate in edge_obj.predicates:
                                    descendants = self._biolink_category_descendent_lookup(predicate.passed_name)
                                    if "biolink:genetically_interacts_with" in descendants:
                                        predicate_descendent_found = True
                                        edge_obj.set_predicates("biolink:genetically_interacts_with")
                                        self.query_graph.edges[edge] = edge_obj
                                        continue
                                if predicate_descendent_found == False:
                                    passed_names = [predicate.passed_name for predicate in edge_obj.predicates]
                                    raise UnsupportedCategoryAncestors(passed_names)

                if category_ancestor_found == False:
                    passed_names = [category.passed_name for category in node_obj.categories]
                    raise UnsupportedCategoryAncestors(passed_names)
    
    def _process_drug_wildcard_query(self):
        #get nodes
        nodes = self.query_graph.nodes
        #get edges
        edges = self.query_graph.edges
        #loop through nodes and check for appropriate drug descendents
        for node in nodes:
            node_obj = nodes[node]
            if node_obj.ids is None:
                category_descendent_found = False
                for category in node_obj.categories:
                    descendants = self._biolink_category_descendent_lookup(category.passed_name)
                    if "biolink:Drug" in descendants:
                        category_descendent_found = True
                        node_obj.set_categories("biolink:Drug")
                        self.query_graph.nodes[node] = node_obj
                        for edge in edges:
                            edge_obj = edges[edge]
                            object_categories_passed_names = [category.passed_name for category in nodes[edge_obj.object].categories]
                            if edge_obj.subject == node and "biolink:Disease" in object_categories_passed_names:
                                predicate_descendent_found = False
                                for predicate in edge_obj.predicates:
                                    descendants = self._biolink_category_descendent_lookup(predicate.passed_name)
                                    if "biolink:treats" in descendants:
                                        predicate_descendent_found = True
                                        edge_obj.set_predicates("biolink:treats")
                                        self.query_graph.edges[edge] = edge_obj
                                        continue
                                if predicate_descendent_found == False:
                                    passed_names = [predicate.passed_name for predicate in edge_obj.predicates]
                                    raise UnsupportedPredicateAncestor(passed_names)
                            elif edge_obj.subject == node and "biolink:Gene" in object_categories_passed_names:
                                predicate_descendent_found = False
                                for predicate in edge_obj.predicates:
                                    descendants = self._biolink_category_descendent_lookup(predicate.passed_name)
                                    if "biolink:interacts_with" in descendants:
                                        predicate_descendent_found = True
                                        edge_obj.set_predicates("biolink:interacts_with")
                                        self.query_graph.edges[edge] = edge_obj
                                        continue
                                if predicate_descendent_found == False:
                                    passed_names = [predicate.passed_name for predicate in edge_obj.predicates]
                                    raise UnsupportedPredicateAncestor(passed_names)
                if category_descendent_found == False:
                    passed_names = [category.passed_name for category in node_obj.categories]
                    raise UnsupportedCategoryAncestors(passed_names)
                continue
    
    def _process_wildcard_proxy(self):
        #get eges
        edges = self.query_graph.edges
        #get nodes
        nodes = self.query_graph.nodes

        for node in nodes:
            node_obj = nodes[node]
            if node_obj.ids == None:    
                #find edge for this node
                for edge in edges:
                    edge_obj = edges[edge]
                    if edge_obj.subject == node:
                        #check constraints for context
                        drug_constraint = edge_obj.find_constraint("drug")
                        gene_constraint = edge_obj.find_constraint("gene")
                        #gene wildcard by drug found in constraint
                        if drug_constraint is not None:
                            category_descendent_found = False
                            for category in node_obj.categories:
                                descendants = self._biolink_category_descendent_lookup(category.passed_name)
                                if "biolink:Gene" in descendants:
                                    node_obj.set_categories("biolink:Gene")
                            if category_descendent_found == False:
                                raise (node_obj.categories)
                            self.query_graph.nodes[node] = node_obj
                            
                        #drug wildcard by gene found in constraint
                        elif gene_constraint is not None:
                            category_descendent_found = False
                            for category in node_obj.categories:
                                    descendants = self._biolink_category_descendent_lookup(category.passed_name)
                                    if "biolink:Drug" in descendants:
                                        node_obj.set_categories("biolink:Drug")
                            if category_descendent_found == False:
                                passed_names = [category.passed_name for category in node_obj.categories]
                                raise UnsupportedCategoryAncestors(passed_names)
                            self.query_graph.nodes[node] = node_obj
                            
                        else:
                            #in proxy queries without provided context, biolink descendents are only semi-inferable
                            # so long as the passed anscestor does not have both genes and drugs as a child we can still process
                            for category in node_obj.categories:
                                descendants = self._biolink_category_descendent_lookup(category.passed_name)
                                if "biolink:Drug" in descendants and "biolink:Gene" not in descendants:
                                    category_descendent_found = True
                                    node_obj.set_categories("biolink:Drug")
                                elif "biolink:Drug" not in descendants and "biolink:Gene" in descendants:
                                    category_descendent_found = True
                                    node_obj.set_categories("biolink:Gene")
                                elif "biolink:Drug" in descendants and "biolink:Gene" in descendants:
                                    raise IndeterminableCategoryDescendent(node_obj.categories)
                                elif "biolink:Drug" not in descendants and "biolink:Gene" not in descendants:
                                    passed_names = [category.passed_name for category in node_obj.categories]
                                    raise UnsupportedCategoryAncestors(passed_names)
                            self.query_graph.nodes[node] = node_obj
                        #process the predicate    
                        predicate_descendent_found = False
                        if "biolink:Drug" in [category.passed_name for category in nodes[edge_obj.subject].categories] and "biolink:Disease" in [category.passed_name for category in nodes[edge_obj.object].categories]:
                            for predicate in edge_obj.predicates:
                                descendants = self._biolink_category_descendent_lookup(predicate.passed_name)
                                if "biolink:treats" in descendants:
                                    predicate_descendent_found = True
                                    edge_obj.set_predicates("biolink:treats")
                            #if no predicate descendent was found then raise an exception
                            if predicate_descendent_found == False:
                                passed_names = [predicate.passed_name for predicate in edge_obj.predicates]
                                raise UnsupportedPredicateAncestor(passed_names)
                        elif "biolink:Gene" in [category.passed_name for category in nodes[edge_obj.subject].categories] and "biolink:Disease" in [category.passed_name for category in nodes[edge_obj.object].categories]:
                            for predicate in edge_obj.predicates:
                                descendants = self._biolink_category_descendent_lookup(predicate.passed_name)
                                if "biolink:gene_associated_with_condition" in descendants:
                                    predicate_descendent_found = True
                                    edge_obj.set_predicates("biolink:gene_associated_with_condition")
                            #if no predicate descendent was found then raise an exception
                            if predicate_descendent_found == False:
                                passed_names = [predicate.passed_name for predicate in edge_obj.predicates]
                                raise UnsupportedPredicateAncestor(passed_names)
                        elif "biolink:Gene" in [category.passed_name for category in nodes[edge_obj.subject].categories] and "biolink:Drug" in [category.passed_named for category in nodes[edge_obj.object].categories]:
                            for predicate in edge_obj.predicates:
                                descendants = self._biolink_category_descendent_lookup(predicate.passed_name)
                                if "biolink:interacts_with" in descendants:
                                    predicate_descendent_found = True
                                    edge_obj.set_predicates("biolink:interacts_with")
                            #if no predicate descendent was found then raise an exception                                    
                            if predicate_descendent_found == False:
                                passed_names = [predicate.passed_name for predicate in edge_obj.predicates]
                                raise UnsupportedPredicateAncestor(passed_names)
                        elif "biolink:Drug" in [category.passed_name for category in nodes[edge_obj.subject].categories] and "biolink:Gene" in [category.passed_name for category in nodes[edge_obj.object].categories]:
                            for predicate in edge_obj.predicates:
                                descendants = self._biolink_category_descendent_lookup(predicate.passed_name)
                                if "biolink:interacts_with" in descendants:
                                    predicate_descendent_found = True
                                    edge_obj.set_predicates("biolink:interacts_with")
                            #if no predicate descendent was found then raise an exception                                    
                            if predicate_descendent_found == False:
                                passed_names = [predicate.passed_name for predicate in edge_obj.predicates]
                                raise UnsupportedPredicateAncestor(passed_names)
                        self.query_graph.edges[edge] = edge_obj
                        continue   
                continue
    
    def process_biolink_subclasses(self):
        #bools for detimining if drug nodes and gene nodes have been found
        self.drug_nodes_found = False
        self.gene_nodes_found = False

        #process nodes
        self._process_nodes()

        #process edges
        self._process_edges()

        #if query is not a wildcard. graph is fully translated. check if query is a wildcard by checking if gene and drug nodes were found
        #check if gene wildcard query
        if self.drug_nodes_found and not self.gene_nodes_found:
            self._process_gene_wildcard_query()
        #check if grud wildcard query
        elif self.gene_nodes_found and not self.drug_nodes_found:
            self._process_drug_wildcard_query()
        #wildcard proxy queries need to be processed seperately as no gene or drug id is provided
        elif not self.gene_nodes_found and not self.drug_nodes_found:
            self._process_wildcard_proxy()
        
