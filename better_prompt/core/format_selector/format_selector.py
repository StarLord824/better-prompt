"""
Format Selection Module

This module provides intelligent format selection using RAG on the format mapping data.
It recommends the best output format (JSON, XML, YAML, Markdown, etc.) based on
the target model and task type.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, List
import json
import os
from pathlib import Path


class OutputFormat(Enum):
    """Supported output formats."""
    
    JSON = "json"
    XML = "xml"
    YAML = "yaml"
    MARKDOWN = "markdown"
    TEXT = "text"


@dataclass
class FormatRecommendation:
    """
    Result of format selection.
    
    Attributes:
        recommended_format: The recommended output format
        explanation: Why this format was chosen
        template_skeleton: A basic template structure for this format
        confidence: Confidence score (0.0 to 1.0)
        metadata: Additional metadata about the recommendation
    """
    
    recommended_format: OutputFormat
    explanation: str
    template_skeleton: str
    confidence: float
    metadata: Dict[str, any] = None
    
    def __post_init__(self) -> None:
        """Validate confidence score."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        if self.metadata is None:
            self.metadata = {}


class FormatSelector:
    """
    Intelligent format selector using RAG on format mapping data.
    
    This class loads the format mapping (which models prefer which formats)
    and provides recommendations based on the target model and task type.
    """
    
    # Template skeletons for each format
    FORMAT_TEMPLATES: Dict[OutputFormat, str] = {
        OutputFormat.JSON: """{
  "task": "{{task_description}}",
  "requirements": [
    "{{requirement_1}}",
    "{{requirement_2}}"
  ],
  "constraints": {
    "{{constraint_key}}": "{{constraint_value}}"
  },
  "expected_output": "{{output_description}}"
}""",
        
        OutputFormat.XML: """<?xml version="1.0" encoding="UTF-8"?>
<prompt>
  <task>{{task_description}}</task>
  <requirements>
    <requirement>{{requirement_1}}</requirement>
    <requirement>{{requirement_2}}</requirement>
  </requirements>
  <constraints>
    <constraint name="{{constraint_key}}">{{constraint_value}}</constraint>
  </constraints>
  <expected_output>{{output_description}}</expected_output>
</prompt>""",
        
        OutputFormat.YAML: """task: {{task_description}}

requirements:
  - {{requirement_1}}
  - {{requirement_2}}

constraints:
  {{constraint_key}}: {{constraint_value}}

expected_output: {{output_description}}""",
        
        OutputFormat.MARKDOWN: """# Task
{{task_description}}

## Requirements
- {{requirement_1}}
- {{requirement_2}}

## Constraints
{{constraints_list}}

## Expected Output
{{output_description}}""",
        
        OutputFormat.TEXT: """Task: {{task_description}}

Requirements:
- {{requirement_1}}
- {{requirement_2}}

Constraints:
- {{constraint_key}}: {{constraint_value}}

Expected Output: {{output_description}}"""
    }
    
    # Format explanations
    FORMAT_EXPLANATIONS: Dict[OutputFormat, str] = {
        OutputFormat.JSON: "JSON format is ideal for structured data, API interactions, and models that excel at parsing hierarchical information.",
        OutputFormat.XML: "XML format is preferred by models trained on structured markup, offering clear hierarchical relationships and metadata support.",
        OutputFormat.YAML: "YAML format provides human-readable structure with minimal syntax, ideal for configuration-style prompts.",
        OutputFormat.MARKDOWN: "Markdown format is excellent for natural language tasks, documentation, and models trained on web content.",
        OutputFormat.TEXT: "Plain text format is universal and works well for simple, conversational prompts without complex structure."
    }
    
    def __init__(self, mapping_path: Optional[str] = None):
        """
        Initialize the FormatSelector.
        
        Args:
            mapping_path: Path to the format mapping JSON file
        """
        if mapping_path is None:
            # Default to the resources directory
            current_dir = Path(__file__).parent.parent
            mapping_path = current_dir / "resources" / "format_mapping.json"
        
        self.mapping_path = Path(mapping_path)
        self.format_mapping = self._load_mapping()
        
        # Build reverse index for faster lookup
        self.model_to_format: Dict[str, str] = {}
        self._build_model_index()
    
    def _load_mapping(self) -> Dict[str, Dict[str, str]]:
        """
        Load the format mapping from JSON file.
        
        Returns:
            Dictionary mapping providers and models to formats
        """
        if not self.mapping_path.exists():
            raise FileNotFoundError(
                f"Format mapping file not found at {self.mapping_path}. "
                "Please ensure format_mapping.json exists in the resources directory."
            )
        
        with open(self.mapping_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _build_model_index(self) -> None:
        """Build a flat index of model names to their preferred formats."""
        for provider, models in self.format_mapping.items():
            for model, format_str in models.items():
                # Store both full name and short name
                full_name = f"{provider.lower()}/{model.lower()}"
                self.model_to_format[full_name] = format_str
                self.model_to_format[model.lower()] = format_str
    
    def recommend_format(
        self,
        model_name: Optional[str] = None,
        provider: Optional[str] = None,
        task_type: Optional[str] = None,
        fallback_format: OutputFormat = OutputFormat.MARKDOWN
    ) -> FormatRecommendation:
        """
        Recommend the best output format for the given parameters.
        
        Args:
            model_name: Name of the target model (e.g., "gpt-4", "claude-3-opus")
            provider: Provider name (e.g., "OpenAI", "Anthropic")
            task_type: Type of task (optional, for future enhancement)
            fallback_format: Format to use if no specific recommendation found
            
        Returns:
            FormatRecommendation with format, explanation, and template
        """
        recommended_format_str = None
        confidence = 0.5
        explanation_parts = []
        
        # Try to find format based on model and provider
        if model_name:
            model_lower = model_name.lower()
            
            # Try full provider/model lookup
            if provider:
                full_key = f"{provider.lower()}/{model_lower}"
                if full_key in self.model_to_format:
                    recommended_format_str = self.model_to_format[full_key]
                    confidence = 1.0
                    explanation_parts.append(
                        f"Based on format mapping, {provider} {model_name} prefers {recommended_format_str}"
                    )
            
            # Try model name only
            if not recommended_format_str and model_lower in self.model_to_format:
                recommended_format_str = self.model_to_format[model_lower]
                confidence = 0.9
                explanation_parts.append(
                    f"Based on format mapping, {model_name} prefers {recommended_format_str}"
                )
            
            # Try partial matching
            if not recommended_format_str:
                for model_key, format_str in self.model_to_format.items():
                    if model_lower in model_key or model_key in model_lower:
                        recommended_format_str = format_str
                        confidence = 0.7
                        explanation_parts.append(
                            f"Based on partial match with {model_key}, recommending {recommended_format_str}"
                        )
                        break
        
        # Convert string to OutputFormat enum
        if recommended_format_str:
            try:
                recommended_format = OutputFormat(recommended_format_str.lower())
            except ValueError:
                recommended_format = fallback_format
                confidence = 0.5
                explanation_parts.append(
                    f"Unknown format '{recommended_format_str}', using fallback {fallback_format.value}"
                )
        else:
            recommended_format = fallback_format
            confidence = 0.5
            explanation_parts.append(
                f"No specific format mapping found, using fallback {fallback_format.value}"
            )
        
        # Add format-specific explanation
        explanation_parts.append(self.FORMAT_EXPLANATIONS[recommended_format])
        
        # Get template skeleton
        template_skeleton = self.FORMAT_TEMPLATES[recommended_format]
        
        return FormatRecommendation(
            recommended_format=recommended_format,
            explanation=" ".join(explanation_parts),
            template_skeleton=template_skeleton,
            confidence=confidence,
            metadata={
                "model_name": model_name,
                "provider": provider,
                "task_type": task_type,
                "mapping_source": str(self.mapping_path)
            }
        )
    
    def get_template(self, format_type: OutputFormat) -> str:
        """
        Get the template skeleton for a specific format.
        
        Args:
            format_type: The output format
            
        Returns:
            Template skeleton string
        """
        return self.FORMAT_TEMPLATES.get(format_type, self.FORMAT_TEMPLATES[OutputFormat.TEXT])
    
    def list_supported_models(self) -> List[str]:
        """
        List all models in the format mapping.
        
        Returns:
            List of model identifiers
        """
        models = []
        for provider, provider_models in self.format_mapping.items():
            for model in provider_models.keys():
                models.append(f"{provider}/{model}")
        return sorted(models)
    
    def get_models_by_format(self, format_type: OutputFormat) -> List[str]:
        """
        Get all models that prefer a specific format.
        
        Args:
            format_type: The output format to filter by
            
        Returns:
            List of model identifiers that prefer this format
        """
        matching_models = []
        format_str = format_type.value
        
        for provider, models in self.format_mapping.items():
            for model, model_format in models.items():
                if model_format.lower() == format_str:
                    matching_models.append(f"{provider}/{model}")
        
        return sorted(matching_models)
