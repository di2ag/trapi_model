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
        self.workflow = []

    def add_step(self, workflow_id):
        self.workflow.append(
                WorkflowStep(workflow_id)
                )

    def to_dict(self):
        workflow = [step.to_dict() for step in self.workflow]
        return workflow

