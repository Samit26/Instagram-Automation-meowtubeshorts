# Instagram Cat Content Automation

This project automatically fetches viral cat videos and images from Iposts them to your account with AI-generated captions using the Gemini API.

## Features

- 🐱 **Automated Cat Content**: Fetches viral cat content from popular Instagram accounts
- 🤖 **AI Captions**: Generates engaging captions using Google's Gemini API
- 📅 **Scheduled Posting**: Automatically posts 2 images and 2 reels daily
- 🔄 **Duplicate Prevention**: Tracks posted content to avoid duplicates
- 📊 **Web Monitor**: Real-time dashboard to monitor automation status
- ☁️ **Railway Ready**: Configured for easy deployment on Railway
- 🧪 **Testing Suite**: Comprehensive testing functionality

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env` file and fill in your credentials:

```env
INSTAGRAM_USERNAME=your_instagram_username
INSTAGRAM_PASSWORD=your_instagram_password
GEMINI_API_KEY=your_gemini_api_key
TARGET_ACCOUNTS=cats_of_instagram,catsofinstagram,cat_features
DAILY_IMAGES=2
DAILY_REELS=2
TESTING_MODE=True
```

### 3. Get API Keys

- **Gemini API**: Get free API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Instagram**: Use your regular Instagram credentials

### 4. Test the Setup

```bash
python run_test.py
```

## Usage

### Testing Mode

First, run in testing mode to verify everything works:

```bash
python instagram_automation.py test
```

### Production Mode

Set `TESTING_MODE=False` in `.env` and run:

```bash
python instagram_automation.py
```

### Web Monitor

Monitor your automation with the web dashboard:

```bash
python web_monitor.py
```

Then visit `http://localhost:8000`

## Render Cron Job Deployment

### 🚀 Optimized for Cron Job Execution

The script is now **optimized for external cron job scheduling** and runs perfectly on Render.com:

- **Single Execution Mode**: Runs once per execution and exits cleanly
- **No Internal Scheduling**: Perfect for external cron job systems
- **Automatic Cleanup**: Cleans up files after each run
- **Resource Efficient**: Only uses resources when actively running

### Quick Deploy Guide

1. **Create Render Account**: Sign up at [render.com](https://render.com)
2. **Create Cron Job**: Select "Cron Job" service type
3. **Connect Repository**: Link your GitHub repository
4. **Set Command**: `python enhanced_automation.py`
5. **Configure Schedule**: Use cron expressions like `0 9,15,20 * * *` for 3 times daily
6. **Add Environment Variables**: Set Instagram credentials and API keys

### Detailed Instructions

See **`RENDER_CRON_DEPLOYMENT.md`** for complete step-by-step deployment instructions including:

- Environment variable configuration
- Cron schedule examples
- Monitoring and troubleshooting
- Security best practices

## File Structure

```
Instagram Automation/
├── instagram_automation.py    # Main automation script
├── web_monitor.py            # Web dashboard
├── test_automation.py        # Unit tests
├── run_test.py              # Test runner
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
├── railway.toml            # Railway deployment config
├── downloads/              # Downloaded content
│   ├── images/
│   └── videos/
├── posted/                 # Posted content archive
└── logs/                   # Log files
```

## Configuration

### Target Accounts

Add popular cat accounts to `TARGET_ACCOUNTS`:

- `cats_of_instagram`
- `catsofinstagram`
- `cat_features`
- `cats_of_world`
- `catloversworld`

### Posting Schedule

The automation is designed for cron job execution:

- **Recommended Schedule**: 3 times daily (9 AM, 3 PM, 8 PM UTC)
- **Cron Expression**: `0 9,15,20 * * *`
- **Execution Mode**: Single run per execution (perfect for cron jobs)
- **Auto-cleanup**: Files are cleaned after each posting routine

### Content Filtering

- Minimum likes: 1000 (configurable)
- Avoids duplicate content
- Only fetches recent posts (last 50)

## Safety Features

- **Testing Mode**: Test without actually posting
- **Rate Limiting**: Respects Instagram's rate limits with intelligent backoff
- **Error Handling**: Comprehensive error handling and logging
- **Content Tracking**: Prevents duplicate posts
- **Fallback Captions**: Works even if Gemini API fails
- **Automatic Cleanup**: Removes downloaded files after posting
- **Single Execution**: Perfect for cron job scheduling

## Monitoring

### Web Dashboard Features

- Real-time statistics
- Recent log entries
- Downloaded files list
- Posted content tracking
- Auto-refresh every 30 seconds

### Log Files

All activities are logged to `instagram_automation.log`:

- Content fetching
- Downloads
- Posting attempts
- Errors and warnings

## Testing

### Unit Tests

```bash
python test_automation.py
```

### Integration Test

```bash
python run_test.py
```

### Manual Testing

1. Set `TESTING_MODE=True`
2. Run the automation
3. Check logs for successful fetching
4. Verify downloads in `downloads/` folder

## Troubleshooting

### Common Issues

1. **Instagram Login Failed**

   - Check credentials
   - Enable 2FA and use app password
   - Try logging in manually first

2. **No Content Found**

   - Check target accounts exist
   - Verify accounts are public
   - Lower `MIN_LIKES` threshold

3. **Gemini API Errors**

   - Verify API key is correct
   - Check API quota limits
   - Fallback captions will be used

4. **Railway Deployment Issues**
   - Check environment variables
   - Review Railway logs
   - Verify buildpack detection

### Debug Mode

Enable detailed logging by setting log level to DEBUG in the script.

## Legal and Ethical Considerations

- Respect Instagram's Terms of Service
- Only repost content you have permission to use
- Consider reaching out to original creators
- Use for educational/personal purposes
- Monitor your account for any violations

## License

This project is for educational purposes. Please respect Instagram's terms of service and content creators' rights.

## Support

For issues and questions:

1. Check the logs in `instagram_automation.log`
2. Run the test suite
3. Review Railway deployment logs
4. Check environment variables

## Future Enhancements

- Multi-platform support (Twitter, TikTok)
- Advanced content filtering
- Custom caption templates
- Analytics dashboard
- Mobile app integration
- Content scheduling UI
