
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
from bmt import Toolkit


class Result(TrapiBaseClass):
    def __init__(self, trapi_version, biolink_version):
        self.node_bindings = defaultdict(list)
        self.edge_bindings = defaultdict(list)
        super().__init__(trapi_version, biolink_version)

    def add_node_binding(self, qg_id, kg_id):
        self.node_bindings[qg_id].append(
                Binding(
                    trapi_version,
                    biolink_version,
                    kg_id
                    )
                )
    
    def add_edge_binding(self, qg_id, kg_id):
        self.edge_bindings[qg_id].append(
                Binding(
                    trapi_version,
                    biolink_version,
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

    def load(self, result_info):
        for qg_key, binding_info in result_info["node_bindings"].items():
            _binding = Binding(trapi_version=self.trapi_version, biolink_version=self.biolink_version)
            self.node_bindings[qg_key] = _binding.load(binding_info)
        for qg_key, binding_info in result_info["edge_bindings"].items():
            _binding = Binding(trapi_version=self.trapi_version, biolink_version=self.biolink_version)
            self.edge_bindings[qg_key] = _binding.load(binding_info)
        valid, message = self.validate()
        if valid:
            return self
        else:
            raise InvalidTrapiComponent(self.trapi_version, 'Result', message)

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

    def add_result(self, result):
        self.results.append(result)

    def to_dict(self):
        return [result.to_dict() for result in self.results]

    def load(self, results):
        for result_info in results:
            _result = Result(trapi_version=self.trapi_version, biolink_version=self.biolink_version)
            self.results.append(_result.load(result_info))
        return self

class Binding(TrapiBaseClass):
    def __init__(self, trapi_version, biolink_version, kg_id=None):
        self.id = kg_id
        super().__init__(trapi_version, biolink_version)

    def to_dict(self):
        if self.trapi_version == '1.0' or self.trapi_version == '1.1':
            return {"id": self.id}

    def load(self, binding_info):
        self.id = binding_info.pop("id")
        return self

