# Render.com Configuration

## Web Service Configuration

**Service Type:** Web Service  
**Environment:** Python 3  
**Build Command:** `pip install -r requirements.txt`  
**Start Command:** `python main.py`  

## Environment Variables

Set these in your Render dashboard:

| Variable | Value | Description |
|----------|-------|-------------|
| `WHISPER_MODEL_SIZE` | `small` | Use smaller model for faster startup on Render |
| `WHISPER_DEVICE` | `cpu` | CPU processing (GPU not available on Render) |
| `WHISPER_COMPUTE_TYPE` | `int8` | Efficient computation for CPU |
| `MAX_FILE_SIZE` | `25` | Limit to 25MB for Render constraints |
| `PASS_THRESHOLD` | `70.0` | Minimum passing grade |
| `ALLOWED_ORIGINS` | `https://yourdomain.com,https://yourapp.onrender.com` | Replace with your domains |
| `HOST` | `0.0.0.0` | Required for Render |
| `PORT` | `10000` | Render's default port |

## Render Deployment Steps

### 1. Connect Your Repository

1. Go to [render.com](https://render.com) and sign up/login
2. Click "New +" → "Web Service"
3. Connect your GitHub repository: `Misty-clouds/Quran_grader_API`

### 2. Configure Service Settings

**Basic Settings:**
- **Name:** `quran-grader-api`
- **Region:** Choose closest to your users
- **Branch:** `main`
- **Runtime:** `Python 3`

**Build & Deploy:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python main.py`

**Advanced Settings:**
- **Instance Type:** Standard (512MB RAM minimum for Whisper)
- **Disk:** Default should be sufficient
- **Health Check Path:** `/health`

### 3. Environment Variables

Add the environment variables listed above in the Render dashboard.

### 4. Deploy

Click "Create Web Service" and wait for deployment (first deployment takes 5-10 minutes due to model download).

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
2. **Model Size:** Using `small` instead of `medium` model for faster startup and lower memory usage.
3. **Timeout:** Render has a 30-second timeout for HTTP requests. Audio processing should complete within this limit.

### Cost Optimization

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
