"""
Better Prompt - Example Usage

This script demonstrates how to use the Better Prompt core engine.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from better_prompt.core.classifier import TaskClassifier
from better_prompt.core.format_selector import FormatSelector
from better_prompt.core.refiner import RefinementPipeline, ToneType
from better_prompt.core.pipeline import PipelineOrchestrator
from better_prompt.core.llm_gateway import DummyProvider, LLMProviderFactory


def example_1_task_classification():
    """Example 1: Task Classification"""
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Task Classification")
    print("=" * 60)
    
    classifier = TaskClassifier()
    
    # Test different prompts
    test_prompts = [
        "Write a Python function to calculate fibonacci numbers",
        "Create an image of a sunset over mountains",
        "Translate this text to Spanish",
        "Summarize the key points of this article",
        "SELECT * FROM users WHERE age > 25"
    ]
    
    for prompt in test_prompts:
        result = classifier.classify(prompt)
        print(f"\nPrompt: {prompt}")
        print(f"Task Type: {result.task_type.value}")
        print(f"Confidence: {result.confidence:.2%}")
        print(f"Reasoning: {result.reasoning}")


def example_2_format_selection():
    """Example 2: Format Selection"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Format Selection")
    print("=" * 60)
    
    selector = FormatSelector()
    
    # Test different models
    test_cases = [
        ("gpt-4", "OpenAI"),
        ("claude-3-opus", "Anthropic"),
        ("gemini-pro", "Google"),
        ("deepseek-v3.1", "DeepSeek"),
    ]
    
    for model, provider in test_cases:
        result = selector.recommend_format(model_name=model, provider=provider)
        print(f"\nModel: {provider}/{model}")
        print(f"Recommended Format: {result.recommended_format.value}")
        print(f"Confidence: {result.confidence:.2%}")
        print(f"Explanation: {result.explanation[:100]}...")


def example_3_refinement_pipeline():
    """Example 3: Refinement Pipeline"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Refinement Pipeline")
    print("=" * 60)
    
    # Test with different tones
    test_cases = [
        ("write code to sort array", ToneType.PROFESSIONAL),
        ("explain quantum physics", ToneType.CASUAL),
        ("create api documentation", ToneType.TECHNICAL),
    ]
    
    for prompt, tone in test_cases:
        pipeline = RefinementPipeline(target_tone=tone)
        result = pipeline.refine(prompt)
        
        print(f"\nOriginal: {result.original_prompt}")
        print(f"Tone: {tone.value}")
        print(f"Refined: {result.refined_prompt}")
        print(f"Improvements: {', '.join(result.improvements)}")


def example_4_full_pipeline():
    """Example 4: Full Pipeline Orchestration"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Full Pipeline Orchestration")
    print("=" * 60)
    
    orchestrator = PipelineOrchestrator()
    
    # Process a prompt
    prompt = "create a function that validates email addresses"
    result = orchestrator.process(
        prompt=prompt,
        model_name="gpt-4",
        provider="OpenAI",
        tone=ToneType.PROFESSIONAL,
        apply_template=True
    )
    
    # Print summary
    print(result.get_summary())


def example_5_batch_processing():
    """Example 5: Batch Processing"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Batch Processing")
    print("=" * 60)
    
    orchestrator = PipelineOrchestrator()
    
    prompts = [
        "generate an image of a cat",
        "write sql query to find top customers",
        "debug this python code",
        "translate to french",
        "summarize this article"
    ]
    
    results = orchestrator.process_batch(
        prompts=prompts,
        model_name="gpt-4",
        provider="OpenAI"
    )
    
    # Get statistics
    stats = orchestrator.get_statistics(results)
    
    print("\nBatch Processing Statistics:")
    print(f"Total Prompts: {stats['total_prompts']}")
    print(f"Average Task Confidence: {stats['average_task_confidence']:.2%}")
    print(f"Average Format Confidence: {stats['average_format_confidence']:.2%}")
    print(f"Total Improvements: {stats['total_improvements']}")
    print(f"\nTask Distribution: {stats['task_type_distribution']}")
    print(f"Format Distribution: {stats['format_distribution']}")


def example_6_llm_gateway():
    """Example 6: LLM Gateway (Dummy Provider)"""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: LLM Gateway")
    print("=" * 60)
    
    # Create provider using factory
    provider = LLMProviderFactory.create_provider("dummy")
    
    print(f"Provider: {provider.get_provider_name()}")
    print(f"Available Models: {provider.list_models()}")
    
    # Test completion
    from better_prompt.core.llm_gateway.base import Message, MessageRole
    
    messages = [
        Message(role=MessageRole.SYSTEM, content="You are a helpful assistant."),
        Message(role=MessageRole.USER, content="What is the capital of France?")
    ]
    
    response = provider.completion(
        model="dummy-gpt-4",
        messages=messages,
        temperature=0.7
    )
    
    print(f"\nCompletion Response:")
    print(f"Content: {response.content}")
    print(f"Usage: {response.usage}")


def example_7_format_selector_advanced():
    """Example 7: Advanced Format Selector Features"""
    print("\n" + "=" * 60)
    print("EXAMPLE 7: Advanced Format Selector")
    print("=" * 60)
    
    selector = FormatSelector()
    
    # List all supported models
    print("\nSupported Models:")
    for model in selector.list_supported_models()[:10]:  # Show first 10
        print(f"  - {model}")
    
    # Get models by format
    from better_prompt.core.format_selector import OutputFormat
    
    print(f"\nModels that prefer JSON:")
    for model in selector.get_models_by_format(OutputFormat.JSON):
        print(f"  - {model}")
    
    print(f"\nModels that prefer XML:")
    for model in selector.get_models_by_format(OutputFormat.XML):
        print(f"  - {model}")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("BETTER PROMPT - Core Engine Examples")
    print("=" * 60)
    
    examples = [
        example_1_task_classification,
        example_2_format_selection,
        example_3_refinement_pipeline,
        example_4_full_pipeline,
        example_5_batch_processing,
        example_6_llm_gateway,
        example_7_format_selector_advanced,
    ]
    
    for example in examples:
        try:
            example()
        except Exception as e:
            print(f"\nError in {example.__name__}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
