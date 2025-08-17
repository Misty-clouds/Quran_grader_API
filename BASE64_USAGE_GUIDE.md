# Base64 Audio Endpoint Usage Guide

## Overview

The Quran Grader API now supports base64 encoded audio input through the `/grade_recitation_base64/` endpoint. This is specifically designed for platforms like FlutterFlow that work better with JSON requests rather than multipart form data.

## Endpoints

### 1. Original File Upload Endpoint
- **URL**: `/grade_recitation/`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Use Case**: Direct file uploads, testing with tools like Postman

### 2. New Base64 Audio Endpoint
- **URL**: `/grade_recitation_base64/`
- **Method**: `POST`
- **Content-Type**: `application/json`
- **Use Case**: FlutterFlow, mobile apps, web applications

## Base64 Endpoint Usage

### Request Format

```json
{
  "audio_base64": "UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhY...",
  "compared_letters": "بسم الله الرحمن الرحيم",
  "audio_format": "wav"
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `audio_base64` | string | Yes | Base64 encoded audio data |
| `compared_letters` | string | Yes | Reference Quranic text to compare against |
| `audio_format` | string | No | Audio format (wav, mp3, m4a, etc.) - defaults to "wav" |

### Response Format

```json
{
  "transcribed_text": "بسم الله الرحمن الرحيم",
  "grade": 95.5,
  "is_passed": true,
  "reference_text": "بسم الله الرحمن الرحيم",
  "similarity_score": 0.955,
  "processing_time_ms": 1250
}
```

## FlutterFlow Integration

### 1. API Call Configuration

1. Create a new API call in FlutterFlow
2. Set the following configuration:
   - **Method**: POST
   - **URL**: `https://your-api-domain.com/grade_recitation_base64/`
   - **Headers**: 
     ```
     Content-Type: application/json
     ```

### 2. Request Body

Set the body type to "JSON" and use this structure:

```json
{
  "audio_base64": "[audioBase64Variable]",
  "compared_letters": "[referenceTextVariable]",
  "audio_format": "wav"
}
```

### 3. Variables Setup

Create these variables in FlutterFlow:

- **audioBase64Variable** (String): Contains the base64 encoded audio
- **referenceTextVariable** (String): The Quranic text to compare against

### 4. Response Variables

Map the API response to these variables:

- **transcribedText** (String): `$.transcribed_text`
- **grade** (Double): `$.grade`
- **isPassed** (Boolean): `$.is_passed`
- **similarityScore** (Double): `$.similarity_score`
- **processingTimeMs** (Integer): `$.processing_time_ms`

### 5. Converting Audio to Base64

Since FlutterFlow doesn't directly support converting Uint8List to base64, you'll need to:

1. Create a custom action/function in FlutterFlow
2. Use the `dart:convert` library's `base64Encode()` function
3. Pass the audio bytes and return the base64 string

Example custom action:
```dart
import 'dart:convert';
import 'dart:typed_data';

String convertAudioToBase64(Uint8List audioBytes) {
  return base64Encode(audioBytes);
}
```

## Error Handling

The API returns detailed error messages for common issues:

### 400 Bad Request
- Empty or missing `compared_letters`
- Empty or missing `audio_base64`
- Invalid base64 data
- Audio file too large (>30MB default)

### 500 Internal Server Error
- Speech recognition model not available
- Processing errors

### Example Error Response
```json
{
  "detail": "Invalid base64 audio data. Please ensure the audio is properly encoded."
}
```

## Testing

Use the provided `test_base64_endpoint.py` script to test the endpoint:

```bash
python test_base64_endpoint.py
```

## Data URL Support

The API automatically handles data URLs. If your base64 string includes the data URL prefix, it will be automatically stripped:

```
data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhY...
```

## File Size Limits

- Default maximum file size: 30MB
- This applies to the decoded audio data
- Can be configured via the `MAX_FILE_SIZE` environment variable

## Audio Format Support

The API supports all audio formats that Whisper can process:
- WAV
- MP3
- M4A
- FLAC
- OGG
- And more

The `audio_format` parameter is optional and mainly used for logging purposes.
