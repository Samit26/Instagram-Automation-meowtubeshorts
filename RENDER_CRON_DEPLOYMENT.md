# Instagram Automation - Render Cron Job Deployment Guide

## 🚀 Complete Deployment Guide for Render.com

This guide will walk you through deploying your Instagram automation script to Render.com using their Cron Job service for scheduled execution.

---

## 📋 Prerequisites

Before you begin, ensure you have:

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Your code needs to be in a GitHub repository
3. **Instagram Credentials**: Valid Instagram username and password
4. **Gemini API Key**: (Optional) For AI caption generation from [Google AI Studio](https://makersuite.google.com/app/apikey)

---

## 🔧 Step 1: Prepare Your Repository

### 1.1 Push Your Code to GitHub

```bash
# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Commit changes
git commit -m "Initial commit - Instagram automation for Render cron"

# Add your GitHub repository as remote
git remote add origin https://github.com/yourusername/your-repo-name.git

# Push to GitHub
git push -u origin main
```

### 1.2 Verify Required Files

Make sure your repository contains:

- ✅ `enhanced_automation.py` (main script)
- ✅ `requirements.txt` (Python dependencies)
- ✅ `.env` file (for local testing - will be ignored on Render)
- ✅ `user_content/` folder structure

---

## 🌐 Step 2: Create Render Cron Job Service

### 2.1 Login to Render Dashboard

1. Go to [render.com](https://render.com)
2. Sign in to your account
3. Click **"New +"** in the top right
4. Select **"Cron Job"**

### 2.2 Connect Your Repository

1. **Connect Repository**: Link your GitHub account and select your repository
2. **Name**: Give your cron job a descriptive name (e.g., "instagram-automation-cron")
3. **Branch**: Select `main` (or your default branch)
4. **Runtime**: Select **"Python 3"**

### 2.3 Configure Cron Job Settings

**Command to Run:**

```bash
python enhanced_automation.py
```

**Schedule Configuration:**
Choose one of these scheduling options:

#### Option A: Three Times Daily (Recommended)

Create **3 separate cron jobs** for optimal distribution:

1. **Morning Job (9 AM UTC)**

   - Schedule: `0 9 * * *`
   - Name: `instagram-automation-morning`

2. **Afternoon Job (3 PM UTC)**

   - Schedule: `0 15 * * *`
   - Name: `instagram-automation-afternoon`

3. **Evening Job (8 PM UTC)**
   - Schedule: `0 20 * * *`
   - Name: `instagram-automation-evening`

#### Option B: Single Job with Custom Schedule

- **Every 8 hours**: `0 */8 * * *`
- **Twice daily**: `0 9,21 * * *` (9 AM and 9 PM)

---

## 🔐 Step 3: Configure Environment Variables

In your Render dashboard, add these environment variables:

### Required Variables:

| Variable             | Value                     | Description                           |
| -------------------- | ------------------------- | ------------------------------------- |
| `INSTAGRAM_USERNAME` | `your_instagram_username` | Your Instagram login username         |
| `INSTAGRAM_PASSWORD` | `your_instagram_password` | Your Instagram login password         |
| `TESTING_MODE`       | `False`                   | Set to `False` for production posting |

### Optional Variables:

| Variable          | Value                               | Description                          |
| ----------------- | ----------------------------------- | ------------------------------------ |
| `GEMINI_API_KEY`  | `your_gemini_api_key`               | For AI caption generation (optional) |
| `TARGET_ACCOUNTS` | `cats_of_instagram,catsofinstagram` | Cat accounts to fetch from           |
| `DAILY_IMAGES`    | `2`                                 | Target images per day                |
| `DAILY_REELS`     | `2`                                 | Target reels per day                 |

### 3.1 How to Add Environment Variables:

1. In your Render cron job dashboard
2. Go to **"Environment"** tab
3. Click **"Add Environment Variable"**
4. Enter key-value pairs from the table above
5. Click **"Save Changes"**

---

## 🚀 Step 4: Deploy and Test

### 4.1 Initial Deployment

1. Click **"Create Cron Job"**
2. Render will automatically build and deploy your service
3. Monitor the build logs for any errors

### 4.2 Test Your Deployment

**Manual Test Run:**

1. Go to your cron job dashboard
2. Click **"Trigger Job"** to run manually
3. Check the logs to ensure it's working correctly

**Expected Log Output:**

```
Enhanced Instagram Automation started - Single execution mode
🚀 Running posting routine...
Starting optimized posting routine...
🎬 Attempting to fetch new viral cat reels...
✅ Successfully downloaded 1 new viral reels
Posted reel: viral_reel_xxxxx.mp4
🗑️ Successfully cleaned up: viral_reel_xxxxx.mp4
Posted 1 items in this routine
✅ Posting routine completed - Exiting
```

---

## 📊 Step 5: Monitoring and Maintenance

### 5.1 Monitor Logs

**View Real-time Logs:**

1. Go to your cron job dashboard
2. Click on **"Logs"** tab
3. Monitor execution logs for each run

**Key Log Messages to Watch:**

- ✅ `Successfully logged into Instagram`
- ✅ `Downloaded viral reel`
- ✅ `Posted reel/image`
- ✅ `Posting routine completed`
- ⚠️ `Rate limit` (normal, will retry)
- ❌ `Error` messages (need attention)

### 5.2 Performance Monitoring

**Success Indicators:**

- Cron jobs complete within 5-10 minutes
- Content is posted to Instagram
- No persistent error messages
- Storage remains clean (auto-cleanup working)

---

## 🛠️ Step 6: Troubleshooting

### Common Issues and Solutions:

#### 6.1 Instagram Login Failed

**Symptoms:** `Instagram login failed` error in logs

**Solutions:**

1. Verify `INSTAGRAM_USERNAME` and `INSTAGRAM_PASSWORD` are correct
2. Try logging into Instagram manually to check for any security alerts
3. If using 2FA, you may need to use an app-specific password

#### 6.2 No Content Downloaded

**Symptoms:** `No new viral reels could be downloaded` in logs

**Solutions:**

1. This is normal during rate limits - script will retry next run
2. Check if Instagram is blocking requests (try different hashtags)
3. Verify internet connectivity on Render

#### 6.3 Build Failures

**Symptoms:** Deployment fails during build

**Solutions:**

1. Check `requirements.txt` for any invalid packages
2. Ensure Python syntax is correct in `enhanced_automation.py`
3. Review build logs for specific error messages

#### 6.4 Environment Variable Issues

**Symptoms:** Missing configuration errors

**Solutions:**

1. Double-check all environment variables are set correctly
2. Ensure `TESTING_MODE=False` for production
3. Restart cron job after changing environment variables

---

## 🔄 Step 7: Updating Your Deployment

### 7.1 Code Updates

When you need to update your script:

```bash
# Make your changes to the code
git add .
git commit -m "Update automation logic"
git push origin main
```

Render will **automatically redeploy** when you push to your connected branch.

### 7.2 Schedule Changes

To modify the cron schedule:

1. Go to your cron job dashboard
2. Click **"Settings"**
3. Update the **"Schedule"** field
4. Click **"Save Changes"**

---

## 📈 Step 8: Scaling and Optimization

### 8.1 Multiple Accounts

For multiple Instagram accounts:

1. Create separate cron jobs for each account
2. Use different environment variables for each
3. Stagger the schedules to avoid conflicts

### 8.2 Performance Tips

**Optimize for Better Performance:**

- Use shorter execution times by setting `TESTING_MODE=True` initially
- Monitor which hashtags work best and focus on those
- Adjust posting frequency based on your account's growth

---

## 💰 Render Pricing Information

### Free Tier Limitations:

- **750 hours/month** of cron job execution time
- **No cost** for basic cron jobs
- Perfect for this automation (uses ~5-10 minutes per execution)

### Estimated Usage:

- **3 executions/day** × **10 minutes each** = **30 minutes/day**
- **Monthly usage**: ~15 hours (well within free tier)

---

## 🔒 Security Best Practices

### 8.1 Environment Variables

- ✅ Never commit passwords to your repository
- ✅ Use Render's environment variables for all secrets
- ✅ Regularly rotate your Instagram password

### 8.2 Repository Security

- ✅ Add `.env` to your `.gitignore` file
- ✅ Keep your repository private if it contains sensitive logic
- ✅ Use strong, unique passwords for your Instagram account

---

## 📞 Support and Resources

### Getting Help:

1. **Render Documentation**: [render.com/docs](https://render.com/docs)
2. **Render Community**: [community.render.com](https://community.render.com)
3. **Instagram API**: Check Instagram's developer documentation for policy updates

### Useful Commands for Testing:

```bash
# Test locally before deploying
python enhanced_automation.py test

# Check Python syntax
python -m py_compile enhanced_automation.py

# Install dependencies locally
pip install -r requirements.txt
```

---

## ✅ Deployment Checklist

Before going live, ensure:

- [ ] Code is pushed to GitHub
- [ ] Render cron job is created and configured
- [ ] All environment variables are set correctly
- [ ] `TESTING_MODE=False` for production
- [ ] Manual test run completed successfully
- [ ] Cron schedule is set appropriately
- [ ] Logs are being monitored

---

## 🎉 Congratulations!

Your Instagram automation is now running on Render with cron job scheduling!

The system will:

- ✅ Download viral cat content automatically
- ✅ Generate AI captions
- ✅ Post to Instagram 3 times daily
- ✅ Clean up files automatically
- ✅ Handle rate limits gracefully
- ✅ Run reliably in the cloud

**Happy Automating! 🐱✨**
