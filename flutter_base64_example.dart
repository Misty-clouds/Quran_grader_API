// Example of how to use the base64 audio endpoint from Flutter/FlutterFlow
// This code demonstrates the workflow for recording audio and sending it to the API

import 'dart:convert';
import 'dart:typed_data';
import 'package:http/http.dart' as http;

class QuranGraderApiService {
  final String baseUrl;
  
  QuranGraderApiService({required this.baseUrl});
  
  /// Convert audio bytes to base64 and send to the grading API
  Future<GradingResponse> gradeRecitationBase64({
    required Uint8List audioBytes,
    required String comparedLetters,
    String audioFormat = 'wav',
  }) async {
    try {
      // Convert Uint8List to base64
      String audioBase64 = base64Encode(audioBytes);
      
      // Prepare the request body
      Map<String, dynamic> requestBody = {
        'audio_base64': audioBase64,
        'compared_letters': comparedLetters,
        'audio_format': audioFormat,
      };
      
      // Make the API call
      final response = await http.post(
        Uri.parse('$baseUrl/grade_recitation_base64/'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: json.encode(requestBody),
      );
      
      if (response.statusCode == 200) {
        Map<String, dynamic> responseData = json.decode(response.body);
        return GradingResponse.fromJson(responseData);
      } else {
        throw Exception('API Error: ${response.statusCode} - ${response.body}');
      }
    } catch (e) {
      throw Exception('Failed to grade recitation: $e');
    }
  }
  
  /// Health check endpoint
  Future<bool> isApiHealthy() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/health'));
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
}

/// Response model for the grading API
class GradingResponse {
  final String transcribedText;
  final double grade;
  final bool isPassed;
  final String referenceText;
  final double similarityScore;
  final int processingTimeMs;
  
  GradingResponse({
    required this.transcribedText,
    required this.grade,
    required this.isPassed,
    required this.referenceText,
    required this.similarityScore,
    required this.processingTimeMs,
  });
  
  factory GradingResponse.fromJson(Map<String, dynamic> json) {
    return GradingResponse(
      transcribedText: json['transcribed_text'],
      grade: json['grade'].toDouble(),
      isPassed: json['is_passed'],
      referenceText: json['reference_text'],
      similarityScore: json['similarity_score'].toDouble(),
      processingTimeMs: json['processing_time_ms'],
    );
  }
}

/// Example usage in FlutterFlow
class ExampleUsage {
  final QuranGraderApiService apiService = QuranGraderApiService(
    baseUrl: 'https://your-api-domain.com', // Replace with your actual API URL
  );
  
  /// Example method showing how to use the service
  Future<void> gradeUserRecitation() async {
    try {
      // This would typically come from an audio recorder widget in FlutterFlow
      Uint8List audioData = Uint8List(0); // Replace with actual audio data
      String quranicText = "بسم الله الرحمن الرحيم"; // The reference text
      
      // Call the API
      GradingResponse result = await apiService.gradeRecitationBase64(
        audioBytes: audioData,
        comparedLetters: quranicText,
        audioFormat: 'wav',
      );
      
      // Use the results
      print('Transcription: ${result.transcribedText}');
      print('Grade: ${result.grade}%');
      print('Passed: ${result.isPassed}');
      print('Processing time: ${result.processingTimeMs}ms');
      
    } catch (e) {
      print('Error: $e');
    }
  }
}

/*
FlutterFlow Configuration Steps:

1. API Call Configuration:
   - Method: POST
   - URL: https://your-api-domain.com/grade_recitation_base64/
   - Headers: Content-Type: application/json
   
2. Request Body (JSON):
   {
     "audio_base64": "[VARIABLE: audioBase64String]",
     "compared_letters": "[VARIABLE: referenceText]", 
     "audio_format": "wav"
   }

3. Variables needed:
   - audioBase64String (String): base64 encoded audio
   - referenceText (String): Quranic text to compare against

4. Response Variables to create:
   - transcribedText (String)
   - grade (Double) 
   - isPassed (Boolean)
   - referenceText (String)
   - similarityScore (Double)
   - processingTimeMs (Integer)

5. To convert Uint8List to base64 in FlutterFlow:
   - Use a custom action/function that calls base64Encode(audioBytes)
   - Store the result in the audioBase64String variable
*/
