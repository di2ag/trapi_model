
"""
TRAPI Result Data Classes
"""

import json
from jsonschema import ValidationError
from collections import defaultdict

from trapi_model.constants import *
from trapi_model.exceptions import *
from trapi_model.base import TrapiBaseClass

from reasoner_validator import validate_Result_1_0, validate_Result_1_1


class Result(TrapiBaseClass):
    def __init__(self, trapi_version, biolink_version):
        self.node_bindings = defaultdict(list)
        self.edge_bindings = defaultdict(list)
        super().__init__(trapi_version, biolink_version)

    def add_node_binding(self, qg_id, kg_id):
        self.node_bindings[qg_id].append(
                Binding(
                    self.trapi_version,
                    self.biolink_version,
                    kg_id
                    )
                )
    
    def add_edge_binding(self, qg_id, kg_id):
        self.edge_bindings[qg_id].append(
                Binding(
                    self.trapi_version,
                    self.biolink_version,
                    kg_id
                    )
                )

    def to_dict(self):
        return {
                "edge_bindings": {
                    qg_key: [binding.to_dict() \
                            for binding in bindings] \
                            for qg_key, bindings in self.edge_bindings.items()},
                "node_bindings": {
                    qg_key: [binding.to_dict() \
                            for binding in bindings] \
                            for qg_key, bindings in self.node_bindings.items()},
                }

    @staticmethod
    def load(trapi_version, biolink_version, result_info):
        result = Result(trapi_version, biolink_version)
        for qg_key, node_binding_info in result_info["node_bindings"].items():
            node_bindings = []
            for binding_info in node_binding_info:
                node_bindings.append(Binding.load(
                            trapi_version,
                            biolink_version,
                            binding_info,
                            )
                        )
            result.node_bindings[qg_key] = node_bindings
        for qg_key, edge_binding_info in result_info["edge_bindings"].items():
            edge_bindings = []
            for binding_info in edge_binding_info:
                edge_bindings.append(Binding.load(
                            trapi_version,
                            biolink_version,
                            binding_info,
                            )
                        )
            result.edge_bindings[qg_key] = edge_bindings
        valid, message = result.validate()
        if valid:
            return result
        else:
            raise InvalidTrapiComponent(trapi_version, 'Result', message)

    def validate(self):
        _dict = self.to_dict()
        try:
            if self.trapi_version == '1.0':
                validate_Result_1_0(_dict)
            elif self.trapi_version == '1.1':
                validate_Result_1_1(_dict)
            else:
                raise UnsupportedTrapiVersion(self.trapi_version)
            return True, None 
        except ValidationError as ex:
                return False, ex.message

class Results(TrapiBaseClass):
    def __init__(self, trapi_version, biolink_version):
        self.results = []
        super().__init__(trapi_version, biolink_version)

    def add_result(self, node_bindings, edge_bindings):
        result = Result(self.trapi_version, self.biolink_version)
        for qg_id, kg_ids in node_bindings.items():
            for kg_id in kg_ids:
                result.add_node_binding(qg_id, kg_id)
        for qg_id, kg_ids in edge_bindings.items():
            for kg_id in kg_ids:
                result.add_edge_binding(qg_id, kg_id)
        print(json.dumps(result.to_dict(), indent=2))
        self.results.append(result)

    def to_dict(self):
        return [result.to_dict() for result in self.results]

    @staticmethod
    def load(trapi_version, biolink_version, results):
        new_results = Results(trapi_version, biolink_version)
        for result_info in results:
            new_results.results.append(
                    Result.load(
                        trapi_version,
                        biolink_version,
                        result_info,
                        )
                    )
        return new_results

class Binding(TrapiBaseClass):
    def __init__(self, trapi_version, biolink_version, kg_id=None):
        self.id = kg_id
        super().__init__(trapi_version, biolink_version)

        print(json.dumps(self.to_dict(), indent=2))

    def to_dict(self):
        if self.trapi_version == '1.0' or self.trapi_version == '1.1':
            return {"id": self.id}

    @staticmethod
    def load(trapi_version, biolink_version, binding_info):
        print(binding_info)
        kg_id = binding_info.pop("id")
        binding = Binding(trapi_version, biolink_version, kg_id=kg_id)
        return binding

