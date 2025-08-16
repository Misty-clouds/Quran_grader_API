import requests
import json
import time
from pathlib import Path

class TestQuranGraderAPI:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        
    def test_health_check(self):
        """Test API health endpoints"""
        print("Testing health endpoints...")
        
        # Test root endpoint
        response = requests.get(f"{self.base_url}/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print(f"✓ Root endpoint: {data}")
        
        # Test health endpoint
        response = requests.get(f"{self.base_url}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"✓ Health endpoint: {data}")
        
    def test_grading_validation(self):
        """Test request validation"""
        print("\nTesting validation...")
        
        # Test missing reference text
        files = {'audio_file': ('test.wav', b'fake_audio_data', 'audio/wav')}
        data = {'compared_letters': ''}
        response = requests.post(f"{self.base_url}/grade_recitation/", files=files, data=data)
        assert response.status_code == 400
        print("✓ Empty reference text validation")
        
        # Test missing file
        data = {'compared_letters': 'بسم الله'}
        response = requests.post(f"{self.base_url}/grade_recitation/", data=data)
        assert response.status_code == 422  # Unprocessable Entity for missing file
        print("✓ Missing file validation")
        
        # Test invalid file type
        files = {'audio_file': ('test.txt', b'not_audio', 'text/plain')}
        data = {'compared_letters': 'بسم الله'}
        response = requests.post(f"{self.base_url}/grade_recitation/", files=files, data=data)
        assert response.status_code == 400
        print("✓ Invalid file type validation")
        
    def test_cors_headers(self):
        """Test CORS configuration"""
        print("\nTesting CORS headers...")
        
        response = requests.options(f"{self.base_url}/grade_recitation/")
        headers = response.headers
        
        # Check for CORS headers
        assert 'access-control-allow-origin' in headers
        assert 'access-control-allow-methods' in headers
        print("✓ CORS headers present")
        
    def create_sample_audio(self):
        """Create a small WAV file for testing"""
        # This creates a minimal valid WAV file header
        wav_header = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x22\x56\x00\x00\x44\xac\x00\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
        return wav_header
        
    def test_grading_endpoint(self):
        """Test the main grading functionality"""
        print("\nTesting grading endpoint...")
        
        # Create a sample audio file
        audio_data = self.create_sample_audio()
        
        files = {'audio_file': ('test.wav', audio_data, 'audio/wav')}
        data = {'compared_letters': 'بسم الله الرحمن الرحيم'}
        
        start_time = time.time()
        response = requests.post(f"{self.base_url}/grade_recitation/", files=files, data=data)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Grading successful: {result}")
            print(f"  Response time: {(end_time - start_time)*1000:.0f}ms")
            
            # Validate response structure
            required_fields = ['transcribed_text', 'grade', 'is_passed', 'reference_text', 'similarity_score', 'processing_time_ms']
            for field in required_fields:
                assert field in result, f"Missing field: {field}"
            
            # Validate data types
            assert isinstance(result['grade'], (int, float))
            assert isinstance(result['is_passed'], bool)
            assert isinstance(result['similarity_score'], (int, float))
            assert isinstance(result['processing_time_ms'], int)
            
            print("✓ Response structure validated")
        else:
            print(f"✗ Grading failed: {response.status_code} - {response.text}")
            
    def test_load_testing(self, num_requests=5):
        """Basic load testing"""
        print(f"\nTesting with {num_requests} concurrent requests...")
        
        import concurrent.futures
        
        def make_request():
            audio_data = self.create_sample_audio()
            files = {'audio_file': ('test.wav', audio_data, 'audio/wav')}
            data = {'compared_letters': 'الله'}
            
            start = time.time()
            response = requests.post(f"{self.base_url}/grade_recitation/", files=files, data=data)
            end = time.time()
            
            return response.status_code, end - start
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_requests) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        success_count = sum(1 for status, _ in results if status == 200)
        avg_time = sum(time for _, time in results) / len(results)
        
        print(f"✓ Load test completed: {success_count}/{num_requests} successful")
        print(f"  Average response time: {avg_time*1000:.0f}ms")
        
    def run_all_tests(self):
        """Run all tests"""
        print("Starting API tests...\n")
        
        try:
            self.test_health_check()
            self.test_grading_validation()
            self.test_cors_headers()
            self.test_grading_endpoint()
            self.test_load_testing()
            
            print("\n🎉 All tests passed!")
            
        except AssertionError as e:
            print(f"\n❌ Test failed: {e}")
        except requests.exceptions.ConnectionError:
            print("\n❌ Connection failed. Make sure the API is running!")
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    # You can change the URL if testing a remote server
    tester = TestQuranGraderAPI("http://localhost:8000")
    tester.run_all_tests()
