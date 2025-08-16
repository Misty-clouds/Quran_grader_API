import 'dart:io';
import 'dart:typed_data';
import 'dart:convert';
import 'dart:math';

class QuranGraderClient {
  final String baseUrl;
  final HttpClient _httpClient;
  final int maxRetries;
  final Duration baseDelay;

  QuranGraderClient({
    required this.baseUrl,
    Duration timeout = const Duration(seconds: 30),
    this.maxRetries = 3,
    this.baseDelay = const Duration(seconds: 2),
  }) : _httpClient = HttpClient() {
    _httpClient.connectionTimeout = timeout;
  }

  /// Grade a Quranic recitation with retry logic for 500 students
  Future<GradingResult> gradeRecitation({
    required Uint8List audioBytes,
    required String referenceText,
    String filename = 'audio.wav',
    Function(String)? onStatusUpdate,
  }) async {
    for (int attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        onStatusUpdate?.call(attempt == 1 
            ? 'Processing recitation...' 
            : 'Retrying... (attempt $attempt/$maxRetries)');
            
        final result = await _performGrading(
          audioBytes: audioBytes,
          referenceText: referenceText,
          filename: filename,
        );
        
        onStatusUpdate?.call('Grading completed successfully!');
        return result;
        
      } catch (e) {
        if (attempt == maxRetries) {
          onStatusUpdate?.call('Failed to process recitation. Please try again.');
          rethrow;
        }
        
        // Exponential backoff with jitter for 500 students
        final delay = Duration(
          milliseconds: (baseDelay.inMilliseconds * pow(2, attempt - 1)).round() +
                       Random().nextInt(1000)
        );
        
        onStatusUpdate?.call('Server busy, waiting ${delay.inSeconds}s before retry...');
        await Future.delayed(delay);
      }
    }
    
    throw GradingException('Maximum retry attempts exceeded');
  }

  Future<GradingResult> _performGrading({
    required Uint8List audioBytes,
    required String referenceText,
    required String filename,
  }) async {
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
    } else if (response.statusCode == 429) {
      // Rate limited - specific handling for high load
      throw GradingException('Server is busy. Please wait before trying again.');
    } else if (response.statusCode >= 500) {
      // Server error - retry these
      throw GradingException('Server error. Retrying...');
    } else {
      // Client error - don't retry these
      final errorBody = await response.transform(utf8.decoder).join();
      throw GradingException('Request failed: $errorBody', shouldRetry: false);
    }
  }

  /// Check if the API is healthy - important for 500 students
  Future<HealthStatus> checkHealth() async {
    try {
      final uri = Uri.parse('$baseUrl/health');
      final request = await _httpClient.getUrl(uri);
      final response = await request.close();
      
      if (response.statusCode == 200) {
        final responseBody = await response.transform(utf8.decoder).join();
        final healthData = json.decode(responseBody);
        return HealthStatus.fromJson(healthData);
      } else {
        return HealthStatus(
          status: 'unhealthy',
          modelStatus: 'unknown',
          message: 'HTTP ${response.statusCode}',
        );
      }
    } catch (e) {
      return HealthStatus(
        status: 'unhealthy',
        modelStatus: 'unknown',
        message: e.toString(),
      );
    }
  }

  /// Get server load info (useful for 500 students)
  Future<bool> isServerReady() async {
    final health = await checkHealth();
    return health.status == 'healthy' && health.modelStatus == 'loaded';
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

class HealthStatus {
  final String status;
  final String modelStatus;
  final String? message;
  final Map<String, dynamic>? configuration;

  HealthStatus({
    required this.status,
    required this.modelStatus,
    this.message,
    this.configuration,
  });

  factory HealthStatus.fromJson(Map<String, dynamic> json) {
    return HealthStatus(
      status: json['status'] ?? 'unknown',
      modelStatus: json['model_status'] ?? 'unknown',
      configuration: json['configuration'],
    );
  }

  bool get isHealthy => status == 'healthy' && modelStatus == 'loaded';
}

class GradingException implements Exception {
  final String message;
  final bool shouldRetry;

  GradingException(this.message, {this.shouldRetry = true});

  @override
  String toString() => 'GradingException: $message';
}

// Queue manager for handling high load (500 students)
class GradingQueue {
  final QuranGraderClient client;
  final int maxConcurrent;
  final List<Future<GradingResult>> _activeRequests = [];

  GradingQueue({
    required this.client,
    this.maxConcurrent = 5, // Limit concurrent requests
  });

  Future<GradingResult> enqueue({
    required Uint8List audioBytes,
    required String referenceText,
    String filename = 'audio.wav',
    Function(String)? onStatusUpdate,
  }) async {
    // Wait if too many active requests
    while (_activeRequests.length >= maxConcurrent) {
      onStatusUpdate?.call('Waiting in queue... (${_activeRequests.length} ahead)');
      await Future.any(_activeRequests);
      // Clean up completed requests
      _activeRequests.clear();
    }

    final request = client.gradeRecitation(
      audioBytes: audioBytes,
      referenceText: referenceText,
      filename: filename,
      onStatusUpdate: onStatusUpdate,
    );

    _activeRequests.add(request);

    try {
      return await request;
    } finally {
      _activeRequests.remove(request);
    }
  }
}

// Usage example for 500 students:
/*
final client = QuranGraderClient(
  baseUrl: 'https://your-service-name.onrender.com',
  maxRetries: 3,  // Important for high load
);

final queue = GradingQueue(
  client: client,
  maxConcurrent: 5,  // Prevent overwhelming server
);

try {
  // Check server health first
  final health = await client.checkHealth();
  if (!health.isHealthy) {
    print('Server not ready: ${health.message}');
    return;
  }

  // Use queue for high load scenarios
  final result = await queue.enqueue(
    audioBytes: audioFileBytes,
    referenceText: 'بسم الله الرحمن الرحيم',
    onStatusUpdate: (status) => print(status),
  );
  
  print('Grade: ${result.grade}%');
  print('Passed: ${result.isPassed}');
  print('Processing time: ${result.processingTimeMs}ms');
  
} catch (e) {
  print('Error: $e');
} finally {
  client.dispose();
}
*/
