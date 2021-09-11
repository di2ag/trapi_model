import os
import json
import trapi_model
from trapi_model.base import TrapiBaseClass

WORKFLOW_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'schemas/workflow.json'))

class WorkflowStep(TrapiBaseClass):
    def __init__(self, workflow_id):
        self.workflow_id = workflow_id

    def to_dict(self):
        return {"id": self.workflow_id}
    
    @staticmethod
    def load_workflow_step(workflow_step_dict):
        workflow_id = workflow_step_dict.pop("id")
        return WorkflowStep(
                workflow_id
                )

class Workflow(TrapiBaseClass):
    def __init__(self):
        self.workflow_file = open(WORKFLOW_PATH, 'r')
        self.workflow = json.load(self.workflow_file)
        self.workflow_file.close()
        self.query_workflow = []
        self.max_results = 10
        self.workflow_steps = []

    def add_step(self, workflow_id):
        self.workflow_steps.append(
                WorkflowStep(workflow_id)
                )

    def to_dict(self):
        workflow_steps = [step.to_dict() for step in self.workflow_steps]
        return workflow_steps

    def check_workflow(self):
        operations_dict = self.workflow.pop('workflow')
        operations_terms = []
        for operation in operations_dict:
            operation_term = operation.pop('id')
            operations_terms.append(operation_term)

        for operation in self.query_workflow:
            operation_term = operation.pop('id', None)
            if operation_term == 'filter_results_top_n':
                param = operation.pop('parameters')
                self.max_results = param.pop('max_results')
            if operation_term not in operations_terms:
                raise Exception('Workflow Error: Connections Hypothesis Provider does not handle {} operations'.format(operation_term))


