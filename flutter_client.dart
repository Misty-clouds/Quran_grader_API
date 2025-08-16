import 'dart:io';
import 'dart:typed_data';
import 'dart:convert';

class QuranGraderClient {
  final String baseUrl;
  final HttpClient _httpClient;

  QuranGraderClient({
    required this.baseUrl,
    Duration timeout = const Duration(seconds: 30),
  }) : _httpClient = HttpClient() {
    _httpClient.connectionTimeout = timeout;
  }

  /// Grade a Quranic recitation
  Future<GradingResult> gradeRecitation({
    required Uint8List audioBytes,
    required String referenceText,
    String filename = 'audio.wav',
  }) async {
    try {
      final uri = Uri.parse('$baseUrl/grade_recitation/');
      final request = await _httpClient.postUrl(uri);

      // Set headers
      request.headers.set('Content-Type', 'multipart/form-data; boundary=----boundary');

      // Create multipart form data
      final boundary = '----boundary';
      final formData = <int>[];

      // Add compared_letters field
      formData.addAll('--$boundary\r\n'.codeUnits);
      formData.addAll('Content-Disposition: form-data; name="compared_letters"\r\n\r\n'.codeUnits);
      formData.addAll('$referenceText\r\n'.codeUnits);

      // Add audio file
      formData.addAll('--$boundary\r\n'.codeUnits);
      formData.addAll('Content-Disposition: form-data; name="audio_file"; filename="$filename"\r\n'.codeUnits);
      formData.addAll('Content-Type: audio/wav\r\n\r\n'.codeUnits);
      formData.addAll(audioBytes);
      formData.addAll('\r\n'.codeUnits);
      formData.addAll('--$boundary--\r\n'.codeUnits);

      // Send request
      request.add(formData);
      final response = await request.close();

      if (response.statusCode == 200) {
        final responseBody = await response.transform(utf8.decoder).join();
        final jsonData = json.decode(responseBody);
        return GradingResult.fromJson(jsonData);
      } else {
        final errorBody = await response.transform(utf8.decoder).join();
        throw GradingException('HTTP ${response.statusCode}: $errorBody');
      }
    } catch (e) {
      throw GradingException('Failed to grade recitation: $e');
    }
  }

  /// Check if the API is healthy
  Future<bool> checkHealth() async {
    try {
      final uri = Uri.parse('$baseUrl/health');
      final request = await _httpClient.getUrl(uri);
      final response = await request.close();
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  void dispose() {
    _httpClient.close();
  }
}

class GradingResult {
  final String transcribedText;
  final double grade;
  final bool isPassed;
  final String referenceText;
  final double similarityScore;
  final int processingTimeMs;

  GradingResult({
    required this.transcribedText,
    required this.grade,
    required this.isPassed,
    required this.referenceText,
    required this.similarityScore,
    required this.processingTimeMs,
  });

  factory GradingResult.fromJson(Map<String, dynamic> json) {
    return GradingResult(
      transcribedText: json['transcribed_text'] ?? '',
      grade: (json['grade'] ?? 0).toDouble(),
      isPassed: json['is_passed'] ?? false,
      referenceText: json['reference_text'] ?? '',
      similarityScore: (json['similarity_score'] ?? 0).toDouble(),
      processingTimeMs: json['processing_time_ms'] ?? 0,
    );
  }
}

class GradingException implements Exception {
  final String message;
  GradingException(this.message);

  @override
  String toString() => 'GradingException: $message';
}

// Usage example for Render deployment:
/*
final client = QuranGraderClient(
  baseUrl: 'https://your-service-name.onrender.com'  // Replace with your Render URL
);

try {
  // Check if API is available
  final isHealthy = await client.checkHealth();
  if (!isHealthy) {
    print('API is not available. Please check your connection.');
    return;
  }

  final result = await client.gradeRecitation(
    audioBytes: audioFileBytes,
    referenceText: 'بسم الله الرحمن الرحيم',
  );
  
  print('Grade: ${result.grade}%');
  print('Passed: ${result.isPassed}');
  print('Transcribed: ${result.transcribedText}');
  print('Processing time: ${result.processingTimeMs}ms');
} catch (e) {
  print('Error: $e');
} finally {
  client.dispose();
}
*/
