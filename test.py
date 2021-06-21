from trapi_model.query_graph import QueryGraph

qg ={
                   "nodes": {
                "n0": {
                    "ids": [
                        "MONDO:0007254"
                    ],
                    "categories": [
                        "biolink:Gene"
                    ],
                    "constraints": []
                },
                "n1": {
                    "ids": [
                        "CHEMBL:CHEMBL3545252"
                    ],
                    "categories": [
                        "biolink:Drug"
                    ],
                    "constraints": []
                },
                "n2": {
                    "ids": [
                        "EFO:0000714"
                    ],
                    "categories": [
                        "biolink:PhenotypicFeature"
                    ],
                    "constraints": []
                },
                "n3": {
                    "ids": None,
                    "categories": [
                        "biolink:Gene"
                    ],
                    "constraints": []
                }
            },
            "edges": {
                "e0": {
                    "predicates": [
                        "biolink:treats"
                    ],
                    "relation": None,
                    "subject": "n1",
                    "object": "n0",
                    "constraints": []
                },
                "e1": {
                    "predicates": [
                        "biolink:has_phenotype"
                    ],
                    "relation": None,
                    "subject": "n0",
                    "object": "n2",
                    "constraints": [
                        {
                            "name": "survival_time",
                            "id": "EFO:0000714",
                            "operator": ">",
                            "value": 3736,
                            "unit_id": None,
                            "unit_name": None,
                            "not": False
                        }
                    ]
                },
                "e2": {
                    "predicates": [
                        "biolink:treats"
                    ],
                    "relation": None,
                    "subject": "n3",
                    "object": "n0",
                    "constraints": []
                }
            }
}

tqg = QueryGraph.load(biolink_version=None, query_graph=qg, trapi_version='1.1')