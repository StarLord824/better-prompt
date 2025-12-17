"""
Refinement Pipeline Module

This module provides a multi-stage prompt refinement pipeline with modular functions
for cleanup, expansion, tone adjustment, token optimization, template application, and validation.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
from enum import Enum
import re


class ToneType(Enum):
    """Supported tone types for prompts."""
    
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    FORMAL = "formal"
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"


@dataclass
class RefinementResult:
    """
    Result of the refinement pipeline.
    
    Attributes:
        refined_prompt: The final refined prompt
        original_prompt: The original input prompt
        stages_applied: List of refinement stages that were applied
        metadata: Metadata from each stage
        improvements: List of improvements made
    """
    
    refined_prompt: str
    original_prompt: str
    stages_applied: List[str] = field(default_factory=list)
    metadata: Dict[str, any] = field(default_factory=dict)
    improvements: List[str] = field(default_factory=list)


class RefinementPipeline:
    """
    Multi-stage prompt refinement pipeline.
    
    The pipeline applies a series of transformations to improve prompt quality:
    1. Cleanup - Remove noise, fix formatting
    2. Expand Constraints - Add missing context and constraints
    3. Tone Adjustment - Adjust tone to match requirements
    4. Token Optimization - Optimize for token efficiency
    5. Apply Template - Structure using format template
    6. Validate - Ensure quality and completeness
    """
    
    def __init__(self, target_tone: ToneType = ToneType.NEUTRAL):
        """
        Initialize the refinement pipeline.
        
        Args:
            target_tone: Desired tone for the refined prompt
        """
        self.target_tone = target_tone
        self.stages: List[Callable] = [
            self._cleanup,
            self._expand_constraints,
            self._adjust_tone,
            self._optimize_tokens,
        ]
    
    def refine(
        self,
        prompt: str,
        task_type: Optional[str] = None,
        format_template: Optional[str] = None,
        custom_constraints: Optional[List[str]] = None
    ) -> RefinementResult:
        """
        Run the full refinement pipeline on a prompt.
        
        Args:
            prompt: The original prompt to refine
            task_type: Type of task (for context-aware refinement)
            format_template: Optional template to apply
            custom_constraints: Additional constraints to add
            
        Returns:
            RefinementResult with refined prompt and metadata
        """
        context = {
            "original_prompt": prompt,
            "current_prompt": prompt,
            "task_type": task_type,
            "format_template": format_template,
            "custom_constraints": custom_constraints or [],
            "improvements": [],
            "stages_applied": [],
            "metadata": {}
        }
        
        # Apply each refinement stage
        for stage in self.stages:
            stage_name = stage.__name__.replace("_", " ").title()
            context = stage(context)
            context["stages_applied"].append(stage_name)
        
        # Apply template if provided
        if format_template:
            context = self._apply_template(context)
            context["stages_applied"].append("Apply Template")
        
        # Validate the result
        context = self._validate(context)
        context["stages_applied"].append("Validate")
        
        return RefinementResult(
            refined_prompt=context["current_prompt"],
            original_prompt=context["original_prompt"],
            stages_applied=context["stages_applied"],
            metadata=context["metadata"],
            improvements=context["improvements"]
        )
    
    def _cleanup(self, context: Dict) -> Dict:
        """
        Stage 1: Clean up the prompt by removing noise and fixing formatting.
        
        Args:
            context: Pipeline context
            
        Returns:
            Updated context
        """
        prompt = context["current_prompt"]
        original = prompt
        
        # Remove excessive whitespace
        prompt = re.sub(r'\s+', ' ', prompt)
        
        # Remove leading/trailing whitespace
        prompt = prompt.strip()
        
        # Fix common typos and formatting issues
        prompt = re.sub(r'\s+([.,!?;:])', r'\1', prompt)  # Remove space before punctuation
        prompt = re.sub(r'([.,!?;:])\s*', r'\1 ', prompt)  # Add space after punctuation
        prompt = prompt.replace('  ', ' ')  # Remove double spaces
        
        # Capitalize first letter
        if prompt and not prompt[0].isupper():
            prompt = prompt[0].upper() + prompt[1:]
        
        if prompt != original:
            context["improvements"].append("Cleaned up formatting and whitespace")
        
        context["current_prompt"] = prompt
        context["metadata"]["cleanup"] = {
            "original_length": len(original),
            "cleaned_length": len(prompt),
            "changes_made": prompt != original
        }
        
        return context
    
    def _expand_constraints(self, context: Dict) -> Dict:
        """
        Stage 2: Expand the prompt with additional constraints and context.
        
        Args:
            context: Pipeline context
            
        Returns:
            Updated context
        """
        prompt = context["current_prompt"]
        task_type = context.get("task_type")
        custom_constraints = context.get("custom_constraints", [])
        has_template = context.get("format_template") is not None
        
        additions = []
        
        # Add task-specific constraints
        if task_type:
            task_constraints = self._get_task_constraints(task_type)
            if task_constraints:
                additions.extend(task_constraints)
        
        # Add custom constraints
        if custom_constraints:
            additions.extend(custom_constraints)
        
        # Only append constraints to prompt if NO template will be used
        # If template exists, constraints will be shown in the template's Constraints section
        if additions and not has_template:
            constraint_text = " ".join(additions)
            prompt = f"{prompt} {constraint_text}"
            context["improvements"].append(
                f"Added {len(additions)} constraint(s) for clarity and specificity"
            )
        elif additions and has_template:
            # Still track that we have constraints, but don't append to prompt
            context["improvements"].append(
                f"Prepared {len(additions)} constraint(s) for template"
            )
        
        context["current_prompt"] = prompt
        context["metadata"]["expand_constraints"] = {
            "constraints_added": len(additions),
            "constraint_list": additions,
            "appended_to_prompt": not has_template
        }
        
        return context
    
    def _get_task_constraints(self, task_type: str) -> List[str]:
        """
        Get task-specific constraints.
        
        Args:
            task_type: Type of task
            
        Returns:
            List of constraint strings
        """
        constraints_map = {
            "code_generation": [
                "Please include comments explaining the logic.",
                "Follow best practices and coding standards.",
                "Ensure the code is production-ready."
            ],
            "image_generation": [
                "Specify the desired style, mood, and composition.",
                "Include details about colors, lighting, and perspective."
            ],
            "research": [
                "Provide sources and citations where applicable.",
                "Include both overview and detailed analysis."
            ],
            "story_writing": [
                "Develop characters with depth and motivation.",
                "Include vivid descriptions and engaging dialogue."
            ],
            "sql_query": [
                "Optimize for performance.",
                "Include comments explaining complex joins or subqueries."
            ],
            "data_analysis": [
                "Provide statistical insights and visualizations if applicable.",
                "Explain methodology and assumptions."
            ]
        }
        
        return constraints_map.get(task_type, [])
    
    def _adjust_tone(self, context: Dict) -> Dict:
        """
        Stage 3: Adjust the tone of the prompt.
        
        Args:
            context: Pipeline context
            
        Returns:
            Updated context
        """
        prompt = context["current_prompt"]
        original = prompt
        
        # Apply tone-specific transformations
        if self.target_tone == ToneType.PROFESSIONAL:
            prompt = self._make_professional(prompt)
        elif self.target_tone == ToneType.CASUAL:
            prompt = self._make_casual(prompt)
        elif self.target_tone == ToneType.TECHNICAL:
            prompt = self._make_technical(prompt)
        elif self.target_tone == ToneType.CREATIVE:
            prompt = self._make_creative(prompt)
        elif self.target_tone == ToneType.FORMAL:
            prompt = self._make_formal(prompt)
        elif self.target_tone == ToneType.FRIENDLY:
            prompt = self._make_friendly(prompt)
        
        if prompt != original:
            context["improvements"].append(f"Adjusted tone to {self.target_tone.value}")
        
        context["current_prompt"] = prompt
        context["metadata"]["adjust_tone"] = {
            "target_tone": self.target_tone.value,
            "tone_changed": prompt != original
        }
        
        return context
    
    def _make_professional(self, prompt: str) -> str:
        """Make prompt more professional."""
        # Remove casual language
        prompt = re.sub(r'\b(kinda|sorta|gonna|wanna)\b', '', prompt, flags=re.IGNORECASE)
        # Add professional framing if very short
        if len(prompt.split()) < 10:
            prompt = f"Please {prompt.lower()}"
        return prompt.strip()
    
    def _make_casual(self, prompt: str) -> str:
        """Make prompt more casual."""
        # Replace formal words with casual equivalents
        replacements = {
            "please provide": "can you give me",
            "kindly": "",
            "request": "ask for"
        }
        for formal, casual in replacements.items():
            prompt = re.sub(formal, casual, prompt, flags=re.IGNORECASE)
        return prompt.strip()
    
    def _make_technical(self, prompt: str) -> str:
        """Make prompt more technical."""
        # Add technical framing
        if not any(word in prompt.lower() for word in ["implement", "develop", "create", "build"]):
            prompt = f"Implement the following: {prompt}"
        return prompt
    
    def _make_creative(self, prompt: str) -> str:
        """Make prompt more creative."""
        # Add creative framing
        if len(prompt.split()) < 15:
            prompt = f"Creatively explore: {prompt}"
        return prompt
    
    def _make_formal(self, prompt: str) -> str:
        """Make prompt more formal."""
        # Remove contractions
        contractions = {
            "don't": "do not",
            "can't": "cannot",
            "won't": "will not",
            "shouldn't": "should not",
            "wouldn't": "would not"
        }
        for contraction, formal in contractions.items():
            prompt = re.sub(contraction, formal, prompt, flags=re.IGNORECASE)
        return prompt
    
    def _make_friendly(self, prompt: str) -> str:
        """Make prompt more friendly."""
        # Add friendly framing
        if not prompt.lower().startswith(("hi", "hello", "hey")):
            prompt = f"Hey! {prompt}"
        return prompt
    
    def _optimize_tokens(self, context: Dict) -> Dict:
        """
        Stage 4: Optimize for token efficiency while preserving meaning.
        
        Args:
            context: Pipeline context
            
        Returns:
            Updated context
        """
        prompt = context["current_prompt"]
        original_length = len(prompt.split())
        
        # Remove redundant words
        redundant_patterns = [
            (r'\b(very|really|quite|rather)\s+', ''),  # Remove intensifiers
            (r'\b(just|simply|basically|actually)\s+', ''),  # Remove filler words
            (r'\bthat\s+', ''),  # Remove unnecessary "that"
        ]
        
        for pattern, replacement in redundant_patterns:
            prompt = re.sub(pattern, replacement, prompt, flags=re.IGNORECASE)
        
        # Clean up any double spaces created
        prompt = re.sub(r'\s+', ' ', prompt).strip()
        
        new_length = len(prompt.split())
        if new_length < original_length:
            context["improvements"].append(
                f"Optimized token usage (reduced from {original_length} to {new_length} words)"
            )
        
        context["current_prompt"] = prompt
        context["metadata"]["optimize_tokens"] = {
            "original_word_count": original_length,
            "optimized_word_count": new_length,
            "reduction_percentage": round((1 - new_length / original_length) * 100, 2) if original_length > 0 else 0
        }
        
        return context
    
    def _apply_template(self, context: Dict) -> Dict:
        """
        Stage 5: Apply a format template to structure the prompt.
        
        Args:
            context: Pipeline context
            
        Returns:
            Updated context
        """
        template = context.get("format_template")
        if not template:
            return context
        
        prompt = context["current_prompt"]
        task_type = context.get("task_type", "general")
        custom_constraints = context.get("custom_constraints", [])
        
        # Extract constraints from the expanded prompt
        constraint_metadata = context.get("metadata", {}).get("expand_constraints", {})
        all_constraints = constraint_metadata.get("constraint_list", [])
        
        # Build replacement dictionary
        replacements = {
            "{{task_description}}": prompt,
            "{{task_type}}": task_type.replace("_", " ").title(),
        }
        
        # Fill in requirements (extract from task-specific constraints)
        requirements = []
        if task_type == "code_generation":
            requirements = [
                "Efficient and optimized implementation",
                "Clear code comments and documentation",
                "Error handling and edge cases covered"
            ]
        elif task_type == "image_generation":
            requirements = [
                "High resolution and quality",
                "Accurate representation of described elements",
                "Professional composition and framing"
            ]
        elif task_type == "sql_query":
            requirements = [
                "Optimized query performance",
                "Proper indexing considerations",
                "Clear result set structure"
            ]
        elif task_type == "data_analysis":
            requirements = [
                "Statistical significance testing",
                "Clear visualizations",
                "Actionable insights"
            ]
        else:
            requirements = [
                "Clear and accurate response",
                "Comprehensive coverage of topic",
                "Well-structured output"
            ]
        
        # Add requirement placeholders
        for i, req in enumerate(requirements[:5], 1):  # Max 5 requirements
            replacements[f"{{{{requirement_{i}}}}}"] = req
        
        # Fill remaining requirement slots with empty strings
        for i in range(len(requirements) + 1, 6):
            replacements[f"{{{{requirement_{i}}}}}"] = ""
        
        # Fill in constraints - show all as a formatted list
        if all_constraints:
            # Create a formatted list of all constraints
            constraint_lines = []
            for i, constraint in enumerate(all_constraints, 1):
                constraint_lines.append(f"- {constraint}")
            
            # Join all constraints with newlines
            constraints_text = "\n".join(constraint_lines)
            
            # For single constraint placeholder, use the first one
            replacements["{{constraint_key}}"] = "Requirements"
            replacements["{{constraint_value}}"] = all_constraints[0] if all_constraints else "High quality output required"
            
            # For multi-line constraints (if template supports it)
            replacements["{{constraints_list}}"] = constraints_text
        else:
            replacements["{{constraint_key}}"] = "Quality"
            replacements["{{constraint_value}}"] = "High quality output required"
            replacements["{{constraints_list}}"] = "- High quality output required"
        
        # Fill in output description
        output_descriptions = {
            "code_generation": "Working, well-documented code that meets all requirements",
            "image_generation": "High-quality image matching the description",
            "sql_query": "Optimized SQL query with expected results",
            "data_analysis": "Comprehensive analysis with insights and visualizations",
            "research": "Well-researched content with sources",
            "story_writing": "Engaging narrative with developed characters",
            "translation": "Accurate translation maintaining original meaning",
            "summarization": "Concise summary capturing key points",
        }
        
        replacements["{{output_description}}"] = output_descriptions.get(
            task_type,
            "Clear, accurate, and complete response"
        )
        
        # Apply all replacements
        formatted = template
        for placeholder, value in replacements.items():
            formatted = formatted.replace(placeholder, value)
        
        # Remove any remaining unfilled placeholders
        formatted = re.sub(r'\{\{[^}]+\}\}', '', formatted)
        
        # Clean up any empty lines or excessive whitespace
        formatted = re.sub(r'\n\s*\n\s*\n', '\n\n', formatted)
        formatted = formatted.strip()
        
        context["current_prompt"] = formatted
        context["improvements"].append("Applied format template for structure")
        
        context["metadata"]["apply_template"] = {
            "template_applied": True,
            "template_type": "structured",
            "placeholders_filled": len(replacements)
        }
        
        return context
    
    def _validate(self, context: Dict) -> Dict:
        """
        Stage 6: Validate the refined prompt for quality and completeness.
        
        Args:
            context: Pipeline context
            
        Returns:
            Updated context
        """
        prompt = context["current_prompt"]
        issues = []
        warnings = []
        
        # Check minimum length
        word_count = len(prompt.split())
        if word_count < 5:
            issues.append("Prompt is very short (< 5 words)")
        
        # Check for clarity
        if not any(char in prompt for char in '.!?'):
            warnings.append("Prompt lacks punctuation, may be unclear")
        
        # Check for completeness
        if "{{" in prompt and "}}" in prompt:
            issues.append("Template placeholders not fully replaced")
        
        # Validation passed if no critical issues
        validation_passed = len(issues) == 0
        
        context["metadata"]["validate"] = {
            "validation_passed": validation_passed,
            "word_count": word_count,
            "issues": issues,
            "warnings": warnings
        }
        
        if validation_passed:
            context["improvements"].append("Validation passed - prompt is well-formed")
        
        return context
