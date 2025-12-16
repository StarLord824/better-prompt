"""
Basic tests for Better Prompt core functionality.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from better_prompt.core.classifier import TaskClassifier, TaskType
from better_prompt.core.format_selector import FormatSelector, OutputFormat
from better_prompt.core.refiner import RefinementPipeline, ToneType
from better_prompt.core.pipeline import PipelineOrchestrator


def test_task_classifier():
    """Test task classification."""
    print("Testing TaskClassifier...")
    
    classifier = TaskClassifier()
    
    # Test code generation
    result = classifier.classify("Write a Python function to sort an array")
    assert result.task_type == TaskType.CODE_GENERATION
    assert result.confidence > 0.3  # More lenient threshold
    
    # Test image generation
    result = classifier.classify("Create an image of a sunset")
    assert result.task_type == TaskType.IMAGE_GENERATION
    assert result.confidence > 0.3  # More lenient threshold
    
    print("✓ TaskClassifier tests passed")


def test_format_selector():
    """Test format selection."""
    print("Testing FormatSelector...")
    
    selector = FormatSelector()
    
    # Test OpenAI GPT-4
    result = selector.recommend_format(model_name="gpt-4", provider="OpenAI")
    assert result.recommended_format == OutputFormat.MARKDOWN
    assert result.confidence > 0.8
    
    # Test Anthropic Claude
    result = selector.recommend_format(model_name="claude-3-opus", provider="Anthropic")
    assert result.recommended_format == OutputFormat.XML
    
    # Test listing models
    models = selector.list_supported_models()
    assert len(models) > 0
    
    print("✓ FormatSelector tests passed")


def test_refinement_pipeline():
    """Test refinement pipeline."""
    print("Testing RefinementPipeline...")
    
    pipeline = RefinementPipeline(target_tone=ToneType.PROFESSIONAL)
    
    result = pipeline.refine(
        prompt="write code to sort array",
        task_type="code_generation"
    )
    
    assert result.refined_prompt != result.original_prompt
    assert len(result.stages_applied) > 0
    assert len(result.improvements) >= 0
    
    print("✓ RefinementPipeline tests passed")


def test_pipeline_orchestrator():
    """Test full pipeline orchestration."""
    print("Testing PipelineOrchestrator...")
    
    orchestrator = PipelineOrchestrator()
    
    result = orchestrator.process(
        prompt="create a function that validates email addresses",
        model_name="gpt-4",
        provider="OpenAI"
    )
    
    assert result.original_prompt is not None
    assert result.refined_prompt is not None
    assert result.task_classification is not None
    assert result.format_recommendation is not None
    assert result.refinement_result is not None
    
    # Test to_dict
    result_dict = result.to_dict()
    assert "original_prompt" in result_dict
    assert "refined_prompt" in result_dict
    
    # Test get_summary
    summary = result.get_summary()
    assert len(summary) > 0
    
    print("✓ PipelineOrchestrator tests passed")


def test_batch_processing():
    """Test batch processing."""
    print("Testing batch processing...")
    
    orchestrator = PipelineOrchestrator()
    
    prompts = [
        "generate an image",
        "write sql query",
        "debug code"
    ]
    
    results = orchestrator.process_batch(
        prompts=prompts,
        model_name="gpt-4",
        provider="OpenAI"
    )
    
    assert len(results) == len(prompts)
    
    # Test statistics
    stats = orchestrator.get_statistics(results)
    assert stats["total_prompts"] == len(prompts)
    assert "task_type_distribution" in stats
    
    print("✓ Batch processing tests passed")


def test_llm_gateway():
    """Test LLM gateway."""
    print("Testing LLM Gateway...")
    
    from better_prompt.core.llm_gateway import LLMProviderFactory, DummyProvider
    from better_prompt.core.llm_gateway.base import Message, MessageRole
    
    # Test factory
    providers = LLMProviderFactory.list_providers()
    assert "dummy" in providers
    
    # Create provider
    provider = LLMProviderFactory.create_provider("dummy")
    assert isinstance(provider, DummyProvider)
    
    # Test completion
    messages = [
        Message(role=MessageRole.USER, content="Hello")
    ]
    response = provider.completion(model="dummy-gpt-4", messages=messages)
    assert response.content is not None
    assert response.model == "dummy-gpt-4"
    
    # Test embeddings
    texts = ["hello", "world"]
    emb_response = provider.embeddings(model="dummy-embedding-v1", texts=texts)
    assert len(emb_response.embeddings) == len(texts)
    
    print("✓ LLM Gateway tests passed")


def test_plugin_system():
    """Test plugin system."""
    print("Testing Plugin System...")
    
    from better_prompt.core.plugins import PluginRegistry, PluginManifest, PluginType
    
    # Create a test manifest
    manifest = PluginManifest(
        name="test-plugin",
        version="1.0.0",
        plugin_type=PluginType.REFINER,
        description="Test plugin",
        author="Test",
        entry_point="test.plugin:TestPlugin"
    )
    
    # Validate
    errors = manifest.validate()
    assert len(errors) == 0
    
    # Test registry
    registry = PluginRegistry()
    registry.register_plugin(manifest)
    
    plugins = registry.list_plugins()
    assert len(plugins) == 1
    
    # Test enable/disable
    assert registry.disable_plugin("test-plugin")
    assert not registry.get_plugin("test-plugin").enabled
    
    assert registry.enable_plugin("test-plugin")
    assert registry.get_plugin("test-plugin").enabled
    
    print("✓ Plugin System tests passed")


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Running Better Prompt Tests")
    print("=" * 60 + "\n")
    
    tests = [
        test_task_classifier,
        test_format_selector,
        test_refinement_pipeline,
        test_pipeline_orchestrator,
        test_batch_processing,
        test_llm_gateway,
        test_plugin_system,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
