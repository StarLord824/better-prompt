"""
Test the Better Prompt API endpoints.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("\n" + "="*60)
    print("Testing Health Endpoint")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_info():
    """Test info endpoint."""
    print("\n" + "="*60)
    print("Testing Info Endpoint")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/info")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_process():
    """Test process endpoint."""
    print("\n" + "="*60)
    print("Testing Process Endpoint")
    print("="*60)
    
    data = {
        "prompt": "Write a Python function to validate email addresses",
        "model_name": "gpt-4",
        "provider": "OpenAI",
        "tone": "professional",
        "custom_constraints": ["Use regex", "Add error handling"],
        "apply_template": True
    }
    
    response = requests.post(f"{BASE_URL}/api/v1/process", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    
    print(f"\nOriginal: {result['original_prompt']}")
    print(f"\nTask Type: {result['task_type']} ({result['task_confidence']:.0%})")
    print(f"Format: {result['recommended_format']} ({result['format_confidence']:.0%})")
    print(f"\nRefined Prompt:\n{result['refined_prompt']}")
    print(f"\nImprovements:")
    for imp in result['improvements']:
        print(f"  • {imp}")


def test_classify():
    """Test classify endpoint."""
    print("\n" + "="*60)
    print("Testing Classify Endpoint")
    print("="*60)
    
    data = {"prompt": "Create an image of a sunset over mountains"}
    
    response = requests.post(f"{BASE_URL}/api/v1/classify", json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    
    print(f"Task Type: {result['task_type']}")
    print(f"Confidence: {result['confidence']:.0%}")
    print(f"Reasoning: {result['reasoning']}")


def test_models():
    """Test models endpoint."""
    print("\n" + "="*60)
    print("Testing Models Endpoint")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/v1/models?provider=OpenAI")
    print(f"Status: {response.status_code}")
    models = response.json()
    
    print(f"\nOpenAI Models ({len(models)}):")
    for model in models:
        print(f"  • {model['model']} → {model['preferred_format']}")


def test_providers():
    """Test providers endpoint."""
    print("\n" + "="*60)
    print("Testing Providers Endpoint")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/v1/providers")
    print(f"Status: {response.status_code}")
    providers = response.json()
    
    print(f"\nProviders ({len(providers)}):")
    for provider in providers:
        print(f"  • {provider}")


def test_tones():
    """Test tones endpoint."""
    print("\n" + "="*60)
    print("Testing Tones Endpoint")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/api/v1/tones")
    print(f"Status: {response.status_code}")
    tones = response.json()
    
    print(f"\nAvailable Tones ({len(tones)}):")
    for tone in tones:
        print(f"  • {tone}")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Better Prompt API - Test Suite")
    print("="*60)
    print("\nMake sure the API is running:")
    print("  python run_api.py")
    print("\nPress Enter to start tests...")
    input()
    
    try:
        test_health()
        test_info()
        test_process()
        test_classify()
        test_models()
        test_providers()
        test_tones()
        
        print("\n" + "="*60)
        print("All Tests Completed!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API")
        print("Make sure the API is running: python run_api.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
