
from anki_terminal.metaops.bundles.recipe_description import *
from anki_terminal.metaops.metaop_recipe import MetaOpArgument
from anki_terminal.ops.write.populate_fields import PopulateFieldsOperation
from anki_terminal.ops.write.remove_empty_notes import RemoveEmptyNotesOperation


class RemoveBracketsAndEmptyNotesRecipe(RecipeDescription):

    name = "remove_brackets_and_empty_notes"

    args = [
        MetaOpArgument(
            name="input_file", 
            description="The input file to remove brackets and empty notes from", 
            required=True,
        ),
        MetaOpArgument(
            name="output_file", 
            description="The output file to save the results to", 
            required=True,
        ),
    ]

    targets = [
        TargetDescription(
            type=TargetDescriptionType.BASE_OP_TYPE,
            description=PopulateFieldsOperation,
        ),
        TargetDescription(
            type=TargetDescriptionType.BASE_OP_TYPE,
            description=RemoveEmptyNotesOperation,
        )
    ]
