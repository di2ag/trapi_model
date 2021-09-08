import json
from trapi_model.base import TrapiBaseClass

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
        self.workflow_file = open('../schemas/workflow.json', 'r')
        self.workflow = json.load(self.workflow_file)
        self.query_workflow = dict()
        self.max_results = 10
        self.workflow_steps = []

    def add_step(self, workflow_id):
        self.workflow_steps.append(
                WorkflowStep(workflow_id)
                )

    def to_dict(self):
        workflow_steps = [step.to_dict() for step in self.workflow_steps]
        return workflow

    def check_workflow(self):
        operations_dict = self.workflow.pop('workflow')
        operations_terms = []
        for operation in operations_dict:
            operation_term = operation.pop('id')
            operations_terms.append(operation_term)

        query_operations_dict = self.query_workflow.pop('workflow', dict())
        for operation in query_operations_dict:
            operation_term = operation.pop('id', None)
            if operation_term not in operations_terms:
                raise Exception('Workflow Error: Connections Hypothesis Provider does not handle {} operations'.format(operation_term))

        self.max_results = query_operations_dict.pop('filter_results_top_n', dict()).pop('parameters', dict()).pop('max_results', 10)
        operations = []

