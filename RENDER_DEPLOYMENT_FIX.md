# Quick Render Deployment Fix

## The Error

```
python: can't open file '/opt/render/project/src/app.py': [Errno 2] No such file or directory
```

## The Solution

### Files Added:

1. ✅ `render.yaml` - Render service configuration
2. ✅ `Procfile` - Production start command using Gunicorn

### Render Configuration:

**Service Type**: Web Service
**Environment**: Python 3
**Build Command**: `pip install -r requirements.txt`
**Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`

### Environment Variables to Set in Render:

```
INSTAGRAM_USERNAME=your_username
INSTAGRAM_PASSWORD=your_password
GEMINI_API_KEY=your_api_key
TESTING_MODE=False
TARGET_ACCOUNTS=cats_of_instagram,catsofinstagram
```

### Deploy Steps:

1. **Push to GitHub**:

```bash
git add .
git commit -m "Fix Render deployment with Gunicorn"
git push origin main
```

2. **Redeploy on Render**:

   - Go to your Render dashboard
   - Click "Manual Deploy" or trigger automatic deployment
   - Monitor build logs

3. **Test Deployment**:

```bash
curl https://your-app-name.onrender.com/
curl https://your-app-name.onrender.com/run-task
```

### Expected Success:

- ✅ Build completes without errors
- ✅ App starts with Gunicorn
- ✅ All endpoints respond correctly
- ✅ External cron jobs can trigger `/run-task`

This should resolve the file path issue and get your Flask app running properly on Render!
