from typing import Dict, List
import json
import os
from openai import OpenAI
from anki_types import Note
from .base import FieldPopulator

class JapLlmPopulator(FieldPopulator):
    """A field populator that uses OpenAI's API to analyze Japanese sentences."""
    
    def __init__(self, config_path: str):
        """Initialize the populator from a config file.
        
        The config file should be a JSON file with the following structure:
        {
            "source_field": "Japanese",
            "translation_field": "Translation",
            "breakdown_field": "Breakdown",
            "nuance_field": "Nuance",
            "api_key": "your-api-key-here"  # Optional, can also use OPENAI_API_KEY env var
        }
        """
        try:
            with open(config_path) as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid populator configuration: {str(e)}")
        
        os.environ['OPENAI_LOG'] = 'debug'
            
        required_fields = ["source_field", "translation_field", "breakdown_field", "nuance_field"]
        missing_fields = [f for f in required_fields if f not in config]
        if missing_fields:
            raise ValueError(f"Config missing required fields: {missing_fields}")
            
        self.source_field = config["source_field"]
        self.translation_field = config["translation_field"]
        self.breakdown_field = config["breakdown_field"]
        self.nuance_field = config["nuance_field"]
        
        # Initialize OpenAI client
        api_key = config.get("api_key") or os.getenv("OPENAI_API_KEY")
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
        return [self.translation_field, self.breakdown_field, self.nuance_field]
    
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
    
    def populate_fields(self, note: Note) -> Dict[str, str]:
        """Populate fields for a single note."""
        if self.source_field not in note.fields:
            raise ValueError(f"Source field '{self.source_field}' not found in note")
            
        # Get Japanese text
        japanese_text = note.fields[self.source_field].strip()
        if not japanese_text:
            raise ValueError("Source field is empty")
            
        # Analyze single sentence
        analysis = self._analyze_sentences([japanese_text])[0]
        
        # Format word breakdown
        breakdown = "\n".join(f"• {word['jap']}: {word['eng']}" for word in analysis["words"])
        
        return {
            self.translation_field: analysis["translation"],
            self.breakdown_field: breakdown,
            self.nuance_field: analysis["nuance"]
        }

    def populate_batch(self, notes: List[Note]) -> Dict[int, Dict[str, str]]:
        """Populate fields for a batch of notes.
        
        This is more efficient than processing one note at a time because we:
        1. Send multiple sentences to the API in a single request
        2. Process valid notes in bulk
        3. Skip invalid notes without stopping the batch
        """
        updates = {}
        valid_notes = []
        sentences = []
        
        # Filter valid notes and collect sentences
        for note in notes:
            if self.source_field in note.fields:
                japanese_text = note.fields[self.source_field].strip()
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
                self.translation_field: analysis["translation"],
                self.breakdown_field: breakdown,
                self.nuance_field: analysis["nuance"]
            }
        
        return updates 