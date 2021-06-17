import requests 

meta_knowledge_graph_location = "http://chp.thayer.dartmouth.edu/meta_knowledge_graph/"

response = requests.get(meta_knowledge_graph_location)
meta_knowledge_graph = response.json()

print(meta_knowledge_graph.keys())
edges = meta_knowledge_graph['edges']

for edge in edges:
    print(edge['predicate'])