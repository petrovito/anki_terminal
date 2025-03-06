import json
import os
from typing import Any, Dict, List

from openai import OpenAI

from anki_terminal.anki_types import Model, Note

from .populator_base import FieldPopulator, PopulatorConfigArgument


class JapLlmPopulator(FieldPopulator):
    """A field populator that uses OpenAI's API to analyze Japanese sentences."""
    
    name = "jap-llm"
    description = "Analyze Japanese sentences using OpenAI's API"
    config_args = [
        PopulatorConfigArgument(
            name="source_field",
            description="Field containing Japanese text to analyze",
            required=True
        ),
        PopulatorConfigArgument(
            name="translation_field",
            description="Field to store the English translation",
            required=True
        ),
        PopulatorConfigArgument(
            name="breakdown_field",
            description="Field to store the word breakdown",
            required=True
        ),
        PopulatorConfigArgument(
            name="nuance_field",
            description="Field to store the nuance explanation",
            required=True
        ),
        PopulatorConfigArgument(
            name="api_key",
            description="OpenAI API key (can also use OPENAI_API_KEY env var)",
            required=False,
            default=None
        )
    ]
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the populator with a configuration."""
        super().__init__(config)
        
        os.environ['OPENAI_LOG'] = 'debug'
        
        # Initialize OpenAI client
        api_key = self.config.get("api_key") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key must be provided in config or OPENAI_API_KEY environment variable")
        self.client = OpenAI(api_key=api_key)
    
    @property
    def supports_batching(self) -> bool:
        """Whether this populator supports batch operations."""
        return True
    
    @property
    def target_fields(self) -> List[str]:
        """Get list of fields that will be modified by this populator."""
        return [
            self.config["translation_field"], 
            self.config["breakdown_field"], 
            self.config["nuance_field"]
        ]
    
    def _validate_impl(self, model: Model) -> None:
        """Validate that the source field exists in the model.
        
        Args:
            model: The model to validate against
            
        Raises:
            ValueError: If the source field doesn't exist in the model
        """
        field_names = [f.name for f in model.fields]
        if self.config["source_field"] not in field_names:
            raise ValueError(f"Source field '{self.config['source_field']}' not found in model")
    
    def _analyze_sentences(self, sentences: List[str]) -> List[Dict]:
        """Send sentences to OpenAI API for analysis.
        
        Args:
            sentences: List of Japanese sentences to analyze
            
        Returns:
            List of dictionaries containing translation, word breakdown, and nuance
        """
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "text": """You are assisting users in learning Japanese through real-life examples from anime subtitles. Your task is to analyze Japanese sentences provided as input, and generate comprehensive translations and explanations in JSON format.

**Input:** 
- A JSON list of Japanese sentences that logically follow each other, typically from anime subtitles.

**Output:** 
- A JSON object with a single key "analyses" containing an array where each element corresponds to one input sentence:
  - **translation**: A literal English translation of the sentence.
  - **words**: An array of objects, each explaining a word or phrase from the sentence which aren't particles, names or pronouns:
    -**jap**: The Japanese word or phrase, and the romaji spelling in brackets.
    -**eng**: A short explanation or translation of the word/phrase in English, noting any informal, slang, or cultural nuances.
  - **nuance**: A brief single-sentence string detailing any cultural, contextual, or linguistic nuances not captured by the literal translation. 

Don't list particles, personal pronouns or names!
Example output:
```json
{"analyses":[{"translation":"I didn't die to become an excuse for your suicide.","words":[{"jap":"自殺 (jisatsu)","eng":"suicide; the act of intentionally taking one's own life."},{"jap":"口実 (koujitsu)","eng":"excuse; a reason or justification for doing something, often perceived as insincere or inadequate."},{"jap":"死んだ (shinda)","eng":"died; the past tense of 'to die', indicating the completion of the action."}],"nuance":"The sentence conveys a strong emotional intensity, reflecting an accusation or confrontation."}]}
```
""",
                            "type": "text"
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": json.dumps(sentences, ensure_ascii=False)
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "japformat",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "analyses": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["translation", "words", "nuance"],
                                    "properties": {
                                        "words": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "required": ["jap", "eng"],
                                                "properties": {
                                                    "eng": {"type": "string"},
                                                    "jap": {"type": "string"}
                                                },
                                                "additionalProperties": False
                                            }
                                        },
                                        "nuance": {"type": "string"},
                                        "translation": {"type": "string"}
                                    },
                                    "additionalProperties": False
                                }
                            }
                        },
                        "required": ["analyses"],
                        "additionalProperties": False
                    }
                }
            },
            temperature=0.34,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        
        try:
            response_data = json.loads(response.choices[0].message.content)
            return response_data["analyses"]
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            raise ValueError(f"Failed to parse API response: {str(e)}")
    
    def _populate_fields_impl(self, note: Note) -> Dict[str, str]:
        """Analyze a Japanese sentence and populate fields.
        
        Args:
            note: The note to populate fields for
            
        Returns:
            A dictionary mapping field names to their new values
            
        Raises:
            ValueError: If the source field is not found or empty
        """
        source_field = self.config["source_field"]
        translation_field = self.config["translation_field"]
        breakdown_field = self.config["breakdown_field"]
        nuance_field = self.config["nuance_field"]
        
        if source_field not in note.fields:
            raise ValueError(f"Source field '{source_field}' not found in note")
            
        # Get Japanese text
        japanese_text = note.fields[source_field].strip()
        if not japanese_text:
            raise ValueError("Source field is empty")
            
        # Analyze single sentence
        analysis = self._analyze_sentences([japanese_text])[0]
        
        # Format word breakdown
        breakdown = "\n".join(f"• {word['jap']}: {word['eng']}" for word in analysis["words"])
        
        return {
            translation_field: analysis["translation"],
            breakdown_field: breakdown,
            nuance_field: analysis["nuance"]
        }

    def _populate_batch_impl(self, notes: List[Note]) -> Dict[int, Dict[str, str]]:
        """Analyze multiple Japanese sentences and populate fields.
        
        Args:
            notes: List of notes to populate fields for
            
        Returns:
            Dictionary mapping note IDs to their field updates
            
        Raises:
            ValueError: If the API request fails
        """
        updates = {}
        valid_notes = []
        sentences = []
        
        source_field = self.config["source_field"]
        translation_field = self.config["translation_field"]
        breakdown_field = self.config["breakdown_field"]
        nuance_field = self.config["nuance_field"]
        
        # Filter valid notes and collect sentences
        for note in notes:
            if source_field in note.fields:
                japanese_text = note.fields[source_field].strip()
                if japanese_text:
                    valid_notes.append(note)
                    sentences.append(japanese_text)
        
        if not sentences:
            return updates
            
        # Analyze all sentences in one API call
        analyses = self._analyze_sentences(sentences)
        
        # Process results
        for note, analysis in zip(valid_notes, analyses):
            breakdown = "\n".join(f"• {word['jap']}: {word['eng']}" for word in analysis["words"])
            updates[note.id] = {
                translation_field: analysis["translation"],
                breakdown_field: breakdown,
                nuance_field: analysis["nuance"]
            }
        
        return updates 