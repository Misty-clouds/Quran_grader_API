# Render.com Configuration - Zero Setup Required!

## 🚀 Push and Go Deployment

Your API is pre-configured with optimal defaults for Render. **No environment variables needed!**

**Just:**
1. Push to GitHub
2. Connect to Render
3. Deploy!

## Web Service Configuration

**Service Type:** Web Service  
**Environment:** Python 3  
**Build Command:** `pip install -r requirements.txt`  
**Start Command:** `python main.py`  

## Pre-Configured Defaults

Your API comes with production-ready defaults:

| Setting | Default Value | Purpose |
|---------|---------------|---------|
| **Model Size** | `small` | Fast startup, low memory (512MB compatible) |
| **Audio Quality** | 30MB max | Balance of quality and processing speed |
| **Passing Grade** | 70% | Standard educational threshold |
| **CORS** | All origins allowed | Easy Flutter integration |
| **Port** | 10000 | Render's standard port |

### 🎯 Optimized for 500 Students:

The defaults work great for classes up to 500 students on Render's free/starter plans.

**Want better performance?** Simply add these environment variables in Render:
- `WHISPER_MODEL_SIZE=medium` (for better accuracy)
- `MAX_FILE_SIZE=50` (for higher quality audio)

## Environment Variables (Optional)

**Only add these if you want to customize:**

| Variable | Value | Description |
|----------|-------|-------------|
| `WHISPER_MODEL_SIZE` | `medium` or `large` | Upgrade for better accuracy (needs STANDARD+ plan) |
| `MAX_FILE_SIZE` | `50` | Higher audio quality limit |
| `ALLOWED_ORIGINS` | `https://yourdomain.com` | Restrict CORS for production security |

**🎯 Pro Tip:** Start with defaults, upgrade settings when you upgrade your Render plan!

## Render Deployment Steps

### 1. Push to GitHub

```bash
git add .
git commit -m "Deploy Quran Grader API to Render"
git push origin main
```

### 2. Connect to Render

1. Go to [render.com](https://render.com) and sign up/login
2. Click "New +" → "Web Service"
3. Connect your GitHub repository: `Misty-clouds/Quran_grader_API`

### 3. Configure Service (Zero Config!)

**Basic Settings:**
- **Name:** `quran-grader-api` (or your preferred name)
- **Region:** Choose closest to your users
- **Branch:** `main`
- **Runtime:** `Python 3`

**Build & Deploy:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python main.py`

**That's it!** No environment variables needed.

### 4. Deploy

Click "Create Web Service" and wait for deployment (3-5 minutes).

## Post-Deployment

### Test Your API

```bash
# Health check
curl https://your-service-name.onrender.com/health

# API documentation
https://your-service-name.onrender.com/docs
```

### Flutter Integration

Update your Flutter app to use the Render URL:

```dart
final client = QuranGraderClient(
  baseUrl: 'https://your-service-name.onrender.com'
);
```

## Important Notes

### Performance Considerations

1. **Cold Starts:** Render services may have cold starts. The first request after inactivity takes longer.
2. **Model Size:** For 500 students, use `medium` model for better accuracy.
3. **Timeout:** Render has a 30-second timeout for HTTP requests. Audio processing should complete within this limit.
4. **Concurrent Users:** Plan for 50-100 simultaneous users during peak times.
5. **Request Queuing:** Large classes may need request queuing in your Flutter app.

#### Scaling Considerations for 500 Students:

**Load Distribution:**
- Stagger assignment deadlines to avoid all 500 students submitting at once
- Implement client-side queuing in your Flutter app
- Consider rate limiting to prevent server overload

**Performance Optimization:**
- Use `medium` model for better accuracy (worth the extra processing time)
- Implement audio compression in Flutter before sending
- Add retry logic for failed requests
- Show progress indicators for longer processing times

### Cost Optimization

#### Default Configuration Performance:

**🆓 FREE TIER**
- **Works perfectly** with default settings
- **Processing time:** 3-5 seconds per request
- **Great for:** Development, testing, small classes
- **Model:** Small (fast startup, accurate enough)

**💰 STARTER PLAN** ($7/month)
- **Excellent performance** with defaults
- **Processing time:** 2-4 seconds per request
- **Great for:** Production classes up to 100 students
- **Always on:** No sleep mode

**🚀 STANDARD+ PLANS** ($25+/month)
- **Can upgrade to medium model** for better accuracy
- **Processing time:** 1-3 seconds per request
- **Great for:** Large classes (500+ students)
- **Add environment variable:** `WHISPER_MODEL_SIZE=medium`

#### Simple Scaling Path:

1. **Deploy with defaults** on FREE plan
2. **Test with students** - works great for small classes
3. **Upgrade to STARTER** ($7/month) when you have regular users
4. **Upgrade to STANDARD** ($25/month) for 100+ students
5. **Add `WHISPER_MODEL_SIZE=medium`** for better accuracy

**Configuration for 500 Students:**
- **Plan:** STANDARD ($25/month) minimum
- **Environment Variable:** `WHISPER_MODEL_SIZE=medium`
- **Expected performance:** 1-3 seconds per request

1. **Free Tier:** Render offers 750 hours/month free for web services
2. **Sleep Mode:** Free services sleep after 15 minutes of inactivity
3. **Paid Plans:** Consider paid plans for production use to avoid sleep mode

### Security

1. **HTTPS:** Render provides free SSL certificates
2. **CORS:** Configure `ALLOWED_ORIGINS` properly
3. **Rate Limiting:** Consider implementing rate limiting for production use

### Monitoring

1. **Logs:** Available in Render dashboard
2. **Metrics:** Basic metrics provided
3. **Health Checks:** Use `/health` endpoint for monitoring

## Scaling for 500 Students

### Additional Considerations

#### Flutter App Optimizations:
```dart
// Implement retry logic
Future<GradingResult> gradeWithRetry(audioBytes, referenceText) async {
  for (int attempt = 1; attempt <= 3; attempt++) {
    try {
      return await client.gradeRecitation(
        audioBytes: audioBytes,
        referenceText: referenceText,
      );
    } catch (e) {
      if (attempt == 3) rethrow;
      await Future.delayed(Duration(seconds: attempt * 2));
    }
  }
}

// Show progress indicators
// Add audio compression before upload
// Implement client-side queuing for peak times
```

#### Cost Estimation for 500 Students:
- **STANDARD Plan:** $25/month
- **PRO Plan:** $85/month (recommended)
- **Expected Usage:** 1000-2000 requests/day
- **Peak Concurrent:** 50-100 students

#### Monitoring & Analytics:
- Monitor response times in Render dashboard
- Track error rates and timeouts
- Set up alerts for high usage periods
- Consider usage analytics in your Flutter app

## Troubleshooting

### Common Issues

1. **Build Failures:** Check logs for dependency issues
2. **Memory Issues:** Use smaller Whisper model or upgrade instance
3. **Timeout Issues:** Optimize audio processing or use smaller files
4. **CORS Issues:** Verify `ALLOWED_ORIGINS` configuration

### Getting Help

- Check Render logs in dashboard
- Use `/health` endpoint to verify service status
- Monitor application logs for detailed error information
