from datetime import datetime

from anki_terminal.anki_types import Field, Model, Template
from anki_terminal.changelog import Change, ChangeType
from anki_terminal.ops.op_base import (Operation, OperationArgument,
                                       OperationResult)


class AddModelOperation(Operation):
    """Operation to add a new model with fields and templates."""
    
    name = "add-model"
    description = "Add a new model with the given fields and template"
    readonly = False
    arguments = [
        OperationArgument(
            name="model_name",
            description="Name of the model to create",
            required=True
        ),
        OperationArgument(
            name="fields",
            description="List of field names for the model",
            required=True
        ),
        OperationArgument(
            name="template_name",
            description="Name of the template",
            required=True
        ),
        OperationArgument(
            name="question_format",
            description="Format string for the question side",
            required=True
        ),
        OperationArgument(
            name="answer_format",
            description="Format string for the answer side",
            required=True
        ),
        OperationArgument(
            name="css",
            description="CSS styling for the cards",
            required=True
        )
    ]
    
    def _validate_impl(self) -> None:
        """Validate that the operation can be executed.
        
        Raises:
            ValueError: If arguments are invalid
        """
        # Check if model name already exists
        for model in self.collection.models.values():
            if model.name == self.args["model_name"]:
                raise ValueError(f"Model already exists: {self.args['model_name']}")
        
        # Validate fields list
        if not isinstance(self.args["fields"], list):
            raise ValueError("Fields must be a list")
        if not self.args["fields"]:
            raise ValueError("At least one field is required")
        if len(set(self.args["fields"])) != len(self.args["fields"]):
            raise ValueError("Field names must be unique")
    
    def _execute_impl(self) -> OperationResult:
        """Execute the operation.
        
        Returns:
            OperationResult indicating success/failure and containing changes
        """
        # Generate model ID
        model_id = max(self.collection.models.keys(), default=1000000000) + 1
        
        # Get first available deck ID from collection
        if not self.collection.decks:
            raise RuntimeError("No decks found in collection")
        deck_id = next(iter(self.collection.decks.keys()))
        
        # Create Field objects from field names
        field_objects = [
            Field(
                name=name,
                ordinal=i,
                sticky=False,
                rtl=False,
                font="Arial",
                font_size=20,
                description="",
                plain_text=True
            )
            for i, name in enumerate(self.args["fields"])
        ]
        
        # Create new model
        model = Model(
            id=model_id,
            name=self.args["model_name"],
            fields=field_objects,
            templates=[
                Template(
                    name=self.args["template_name"],
                    question_format=self.args["question_format"],
                    answer_format=self.args["answer_format"],
                    ordinal=0
                )
            ],
            css=self.args["css"],
            deck_id=deck_id,
            modification_time=datetime.now(),
            type=0,  # Standard (not cloze)
            usn=-1,  # -1 indicates needs sync
            version=1  # Start with version 1
        )
        
        # Add model to collection
        self.collection.models[model_id] = model
        
        # Create change record
        change = Change(
            type=ChangeType.MODEL_UPDATED,
            data={
                'models': {
                    str(model_id): model.to_dict()
                    for model_id, model in self.collection.models.items()
                }
            }
        )
        
        return OperationResult(
            success=True,
            message=f"Added model '{self.args['model_name']}' with {len(field_objects)} fields",
            changes=[change]
        ) 