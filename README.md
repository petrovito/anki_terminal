# Anki Terminal

Anki Terminal is a command-line tool for managing Anki packages. It provides a flexible and extensible framework for performing read and write operations on Anki collections.

## Installation

To install the project, clone the repository and install the dependencies:

```bash
git clone https://github.com/petrovito/anki_terminal
cd anki_terminal
pip install .
```

## Project Structure

- **anki_terminal/**: Main module containing the core functionality.
  - **commons/**: Contains common utilities and types used across the project.
  - **persistence/**: Handles database operations and package management.
  - **ops/**: Contains operation definitions and execution logic.
  - **populators/**: Modules for populating data into the Anki collections.
  - **anki_context.py**: Provides the `AnkiContext` class for managing the Anki environment.
  - **main.py**: Entry point for the command-line interface.


## Using AnkiContext

Here's an example of how to use `AnkiContext` in your own project:

```python
from anki_terminal.anki_context import AnkiContext
from anki_terminal.ops import SomeOperation

with AnkiContext(apkg_path='path/to/package.apkg', output_path='path/to/output', read_only=False) as context:
    operation = SomeOperation()
    results = context.run(operation)
    for result in results:
        print(result)
```

## Command Line Tools

The command-line interface provides several options for interacting with Anki packages.

### Read Operations

- **List Operation**: Lists Anki objects at the specified path.
  - **Example Usage**:
    ```bash
    anki-terminal list --path /path/to/anki/objects --limit 10
    ```

- **Count Operation**: Counts Anki objects at the specified path.
  - **Example Usage**:
    ```bash
    anki-terminal count --path /path/to/anki/objects
    ```

#### The `--path` Argument

The `--path` argument is used to specify the location of Anki objects within your collection. It supports various paths, allowing you to target specific models, fields, templates, cards, or notes. Here are some examples of valid paths:

- `/models`: Refers to all models in the collection.
- `/models/Basic`: Refers to the "Basic" model.
- `/models/Basic/fields`: Refers to all fields in the "Basic" model.
- `/models/Basic/fields/Front`: Refers to the "Front" field in the "Basic" model.
- `/models/Basic/templates`: Refers to all templates in the "Basic" model.
- `/models/Basic/templates/Card 1`: Refers to the "Card 1" template in the "Basic" model.
- `/cards`: Refers to all cards in the collection.
- `/notes`: Refers to all notes in the collection.
- `/notes/Basic`: Refers to notes using the "Basic" model.

This flexibility allows you to perform operations on specific parts of your Anki collection, making it easier to manage and modify your data.

### Write Operations

- **Rename Field Operation**: Renames a field in a model and updates all related notes.
  - **Example Usage**:
    ```bash
    anki-terminal rename-field --old-field-name OldName --new-field-name NewName --model-name ModelName
    ```

- **Migrate Notes Operation**: Migrates notes from one model to another with field mapping.
  - **Example Usage**:
    ```bash
    anki-terminal migrate-notes --model-name SourceModel --target-model-name TargetModel --field-mapping '{"sourceField": "targetField"}'
    ```

- **Add Model Operation**: Adds a new model with fields and templates.
  - **Example Usage**:
    ```bash
    anki-terminal add-model --config-file anime_model.json
    ```
    Have a look at `builtin/configs/anime_model.json`

- **Add Field Operation**: Adds a new field to an existing model.
  - **Example Usage**:
    ```bash
    anki-terminal add-field --model-name ModelName --field-name NewField
    ```

- **Tag Notes Operation**: Tags notes based on field data using a regular expression pattern.
  - **Example Usage**:
    ```bash
    anki-terminal tag-notes --model ModelName --source-field FieldName --pattern "regex-pattern"
    ```

### Using Populators

Populators are used to automatically fill or modify fields in your Anki notes based on specific rules or external data sources. They can be configured to perform a variety of tasks, such as copying field values, concatenating fields, or adding language-specific annotations.

Example usage:
```bash
anki-terminal populate-fields <populator_name> --model ModelName --populator-config-file path/to/populator/config.json
```

#### Available Populators

- **Copy Field Populator**: Copies values from one field to another.
  - **Example Config**:
    ```json
    {
      "source_field": "Front",
      "target_field": "Back"
    }
    ```

- **Concat Fields Populator**: Concatenates multiple fields into a target field.
  - **Example Config**:
    ```json
    {
      "source_fields": ["Field1", "Field2"],
      "target_field": "CombinedField",
      "separator": ", "
    }
    ```

- **Jap LLM Populator**: Analyzes Japanese sentences using OpenAI's API.
  - **Example Config**:
    ```json
    {
      "source_field": "JapaneseText",
      "translation_field": "EnglishTranslation",
      "breakdown_field": "WordBreakdown"
    }
    ```

- **Furigana Populator**: Adds furigana readings to Japanese text.
  - **Example Config**:
    ```json
    {
      "source_field": "JapaneseText",
      "target_field": "TextWithFurigana"
    }
    ```

To use a populator, specify it in the command line along with the configuration file:

```bash
anki-terminal populate-fields <populator_name> --config-file path/to/config.json --populator-config-file path/to/populator/config.json
```
