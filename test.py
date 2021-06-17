import requests 

meta_knowledge_graph_location = "http://chp.thayer.dartmouth.edu/meta_knowledge_graph/"

response = requests.get(meta_knowledge_graph_location)
meta_knowledge_graph = response.json()

nodes = meta_knowledge_graph['nodes']

for node in nodes:
    print(nodes[node]['id_prefixes'])