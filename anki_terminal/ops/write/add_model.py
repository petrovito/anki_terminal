from datetime import datetime

from anki_terminal.commons.anki_types import Field, Model, Template
from anki_terminal.commons.changelog import Change, ChangeType
from anki_terminal.ops.op_base import (Operation, OperationArgument,
                                       OperationResult)


class AddModelOperation(Operation):
    """Operation to add a new model with fields and templates."""
    
    name = "add-model"
    description = "Add a new model with the given fields and template"
    readonly = False
    arguments = [
        OperationArgument(
            name="model",
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
        # Check if model already exists
        for model in self.collection.models.values():
            if model.name == self.args["model"]:
                raise ValueError(f"Model '{self.args['model']}' already exists")
        
        # Check if fields list is empty
        if not self.args["fields"]:
            raise ValueError("At least one field is required")
        
        # Check for duplicate field names
        if len(self.args["fields"]) != len(set(self.args["fields"])):
            raise ValueError("Field names must be unique")
    
    def _execute_impl(self) -> OperationResult:
        """Execute the operation.
        
        Returns:
            OperationResult indicating success/failure and containing changes
        """
        # Create new model
        model_id = max(self.collection.models.keys(), default=0) + 1
        model = Model(
            id=model_id,
            name=self.args["model"],
            fields=[],
            templates=[],
            css=self.args["css"],
            deck_id=1,  # Default deck ID
            modification_time=datetime.now(),
            type=0,  # Standard model (not cloze)
            usn=-1,  # Update sequence number
            version=0,  # Version
            latex_pre="\\documentclass[12pt]{article}\n\\special{papersize=3in,5in}\n\\usepackage[utf8]{inputenc}\n\\usepackage{amssymb,amsmath}\n\\pagestyle{empty}\n\\setlength{\\parindent}{0in}\n\\begin{document}\n",
            latex_post="\\end{document}",
            latex_svg=False,
            required=[[0, "all", [0]]],
            tags=[]
        )
        
        # Add fields to model
        for i, field_name in enumerate(self.args["fields"]):
            field = Field(
                name=field_name,
                ordinal=i,
                sticky=False,
                rtl=False,
                font="Arial",
                font_size=20,
                description="",
                plain_text=True
            )
            model.fields.append(field)
        
        # Add template to model
        template = Template(
            name=self.args["template_name"],
            question_format=self.args["question_format"],
            answer_format=self.args["answer_format"],
            ordinal=0,
            deck_override=1,  # Default deck ID
            browser_question_format=None,
            browser_answer_format=None,
            browser_font=None,
            browser_font_size=None
        )
        model.templates.append(template)
        
        # Add model to collection
        self.collection.models[model_id] = model
        
        # Create change record
        change = Change.model_updated(self.collection.models)
        
        return OperationResult(
            success=True,
            message=f"Added model '{model.name}' with {len(model.fields)} fields and 1 template",
            changes=[change]
        ) 