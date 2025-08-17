#!/usr/bin/env python3
"""
Test script for the base64 audio endpoint
This demonstrates how to use the new /grade_recitation_base64/ endpoint
"""

import requests
import base64
import json

def test_base64_endpoint():
    """Test the base64 audio endpoint with a sample audio file"""
    
    # API endpoint
    url = "http://localhost:10000/grade_recitation_base64/"
    
    # Sample Quranic text to compare against
    reference_text = "بسم الله الرحمن الرحيم"
    
    # If you have a sample audio file, you can encode it like this:
    # with open("sample_audio.wav", "rb") as audio_file:
    #     audio_bytes = audio_file.read()
    #     audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
    
    # For this example, we'll create a dummy base64 string
    # In real usage, replace this with actual audio data
    dummy_audio = b"dummy audio data for testing"
    audio_base64 = base64.b64encode(dummy_audio).decode('utf-8')
    
    # Prepare the request payload
    payload = {
        "audio_base64": audio_base64,
        "compared_letters": reference_text,
        "audio_format": "wav"
    }
    
    # Headers
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        # Make the API call
        response = requests.post(url, json=payload, headers=headers)
        
        # Print response
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
    except Exception as e:
        print(f"Error: {e}")

def example_flutterflow_usage():
    """Show how this would be used in FlutterFlow"""
    
    print("\n" + "="*50)
    print("FlutterFlow API Call Configuration:")
    print("="*50)
    
    config = {
        "method": "POST",
        "url": "https://your-api-domain.com/grade_recitation_base64/",
        "headers": {
            "Content-Type": "application/json"
        },
        "body": {
            "audio_base64": "[VARIABLE: base64_encoded_audio]",
            "compared_letters": "[VARIABLE: reference_quranic_text]",
            "audio_format": "wav"
        }
    }
    
    print(json.dumps(config, indent=2))
    
    print("\nFlutterFlow Variables to create:")
    print("- base64_encoded_audio: String (contains the base64 audio data)")
    print("- reference_quranic_text: String (the Quranic text to compare against)")
    
    print("\nExpected Response Structure:")
    response_structure = {
        "transcribed_text": "string",
        "grade": "number (0-100)",
        "is_passed": "boolean",
        "reference_text": "string",
        "similarity_score": "number (0-1)",
        "processing_time_ms": "number"
    }
    print(json.dumps(response_structure, indent=2))

if __name__ == "__main__":
    print("Testing Base64 Audio Endpoint")
    print("=" * 30)
    
    # Note: This will fail with dummy data, but shows the structure
    test_base64_endpoint()
    
    # Show FlutterFlow usage example
    example_flutterflow_usage()
