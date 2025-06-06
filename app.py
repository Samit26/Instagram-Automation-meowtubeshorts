#!/usr/bin/env python3
"""
Flask Web Server for Instagram Automation
Converts the automation script to a web service for Render's free Web Service tier
"""

import os
import sys
import logging
from datetime import datetime
from flask import Flask, jsonify, request
from pathlib import Path
import traceback

# Import our automation class
from enhanced_automation import EnhancedInstagramAutomation

# Initialize Flask app
app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flask_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global automation instance
automation_instance = None


def get_automation_instance():
    """Get or create automation instance"""
    global automation_instance
    if automation_instance is None:
        try:
            logger.info("🔄 Creating automation instance...")
            automation_instance = EnhancedInstagramAutomation()
            logger.info("✅ Automation instance created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create automation instance: {e}")
            logger.error(f"Full error details: {traceback.format_exc()}")
            # Don't raise here - let endpoints handle the error
            return None
    return automation_instance


@app.route('/', methods=['GET'])
def home():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'service': 'Instagram Automation Web Service',
        'message': 'Server is running. Use /run-task to execute automation.',
        'timestamp': datetime.now().isoformat(),
        'endpoints': {
            '/': 'Health check',
            '/run-task': 'Execute automation task',
            '/status': 'Get service status',
            '/logs': 'Get recent logs',
            '/test': 'Test dependencies'
        }
    })


@app.route('/test', methods=['GET'])
def test_dependencies():
    """Test if all dependencies can be imported"""
    results = {}

    # Test core dependencies
    try:
        import flask
        results['flask'] = f"✅ {flask.__version__}"
    except Exception as e:
        results['flask'] = f"❌ {str(e)}"

    try:
        import requests
        results['requests'] = f"✅ {requests.__version__}"
    except Exception as e:
        results['requests'] = f"❌ {str(e)}"

    try:
        from enhanced_automation import EnhancedInstagramAutomation
        results['enhanced_automation'] = "✅ Import successful"
    except Exception as e:
        results['enhanced_automation'] = f"❌ {str(e)}"

    try:
        import instagrapi
        version = getattr(instagrapi, '__version__', 'version unknown')
        results['instagrapi'] = f"✅ {version}"
    except Exception as e:
        results['instagrapi'] = f"❌ {str(e)}"

    try:
        import google.generativeai
        results['google_generativeai'] = "✅ Import successful"
    except Exception as e:
        results['google_generativeai'] = f"❌ {str(e)}"

    try:
        import cv2
        results['opencv'] = f"✅ {cv2.getVersionString()}"
    except Exception as e:
        results['opencv'] = f"❌ {str(e)}"

    # Test environment variables
    env_vars = {
        'INSTAGRAM_USERNAME': bool(os.environ.get('INSTAGRAM_USERNAME')),
        'INSTAGRAM_PASSWORD': bool(os.environ.get('INSTAGRAM_PASSWORD')),
        'GEMINI_API_KEY': bool(os.environ.get('GEMINI_API_KEY')),
        'TESTING_MODE': os.environ.get('TESTING_MODE', 'Not Set'),
        'PORT': os.environ.get('PORT', 'Not Set'),
    }

    return jsonify({
        'status': 'test_complete',
        'dependencies': results,
        'environment_variables': env_vars,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/run-task', methods=['GET'])
def run_task():
    """Execute the Instagram automation task"""
    start_time = datetime.now()
    logger.info(f"🚀 Task execution requested at {start_time.isoformat()}")

    try:
        # Get automation instance
        automation = get_automation_instance()

        if automation is None:
            return jsonify({
                'status': 'error',
                'message': '❌ Failed to initialize automation instance',
                'timestamp': datetime.now().isoformat()
            }), 500

        # Log execution start
        logger.info("📱 Starting Instagram automation task...")

        # Run the posting routine
        automation.enhanced_posting_routine()

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        logger.info(f"✅ Task completed successfully in {duration:.1f} seconds")

        return jsonify({
            'status': 'success',
            'message': '✅ Task executed successfully',
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': round(duration, 1),
            'execution_mode': 'testing' if automation.testing_mode else 'production'
        }), 200

    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        error_trace = traceback.format_exc()

        logger.error(
            f"❌ Task execution failed after {duration:.1f} seconds: {e}")
        logger.error(f"Full traceback: {error_trace}")

        return jsonify({
            'status': 'error',
            'message': f'❌ Task execution failed: {str(e)}',
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': round(duration, 1),
            'error': str(e)
        }), 500


@app.route('/status', methods=['GET'])
def get_status():
    """Get service status and basic info"""
    try:
        # Check if we can create automation instance
        automation = get_automation_instance()

        if automation is None:
            return jsonify({
                'status': 'unhealthy',
                'service': 'Instagram Automation Web Service',
                'message': 'Failed to initialize automation instance',
                'timestamp': datetime.now().isoformat()
            }), 500

        # Get basic status info
        downloads_dir = Path('downloads/videos')
        posted_content_file = Path('posted_content.json')

        downloaded_videos = list(downloads_dir.glob(
            '*.mp4')) if downloads_dir.exists() else []

        # Read posted content count
        posted_count = 0
        if posted_content_file.exists():
            try:
                import json
                with open(posted_content_file, 'r') as f:
                    data = json.load(f)
                    posted_count = len(data.get('videos', [])) + \
                        len(data.get('images', []))
            except:
                posted_count = 0

        return jsonify({
            'status': 'healthy',
            'service': 'Instagram Automation Web Service',
            'testing_mode': automation.testing_mode,
            'username': automation.username,
            'gemini_api_configured': bool(automation.gemini_api_key),
            'stats': {
                'downloaded_videos_available': len(downloaded_videos),
                'total_posted_content': posted_count
            },
            'directories': {
                'downloads_exists': downloads_dir.exists(),
                'user_content_exists': Path('user_content').exists()
            },
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"❌ Status check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'message': f'Service error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/logs', methods=['GET'])
def get_logs():
    """Get recent log entries"""
    try:
        log_file = Path('enhanced_automation.log')
        flask_log_file = Path('flask_automation.log')

        logs = []

        # Read main automation logs (last 50 lines)
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                recent_lines = lines[-50:] if len(lines) > 50 else lines
                logs.extend([line.strip() for line in recent_lines])

        # Read Flask logs (last 20 lines)
        if flask_log_file.exists():
            with open(flask_log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                recent_lines = lines[-20:] if len(lines) > 20 else lines
                logs.extend(
                    [f"[FLASK] {line.strip()}" for line in recent_lines])

        return jsonify({
            'status': 'success',
            'logs': logs[-100:],  # Return last 100 log entries total
            'timestamp': datetime.now().isoformat()
        }), 200

    except Exception as e:
        logger.error(f"❌ Failed to get logs: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve logs: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found',
        'available_endpoints': {
            '/': 'Health check',
            '/run-task': 'Execute automation task',
            '/status': 'Get service status',
            '/logs': 'Get recent logs'
        }
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500


if __name__ == '__main__':
    # Get port from environment variable (Render sets this automatically)
    port = int(os.environ.get('PORT', 5000))

    # Check if running in production (Render) or development
    is_production = os.environ.get('RENDER') is not None

    # Production configuration for Render
    logger.info(f"🚀 Starting Instagram Automation Flask Server on port {port}")
    logger.info(
        f"📱 Environment: {'Production (Render)' if is_production else 'Development'}")
    logger.info(f"📱 Service endpoints available:")
    logger.info(f"   GET  / - Health check")
    logger.info(f"   GET/POST /run-task - Execute automation")
    logger.info(f"   GET  /status - Service status")
    logger.info(f"   GET  /logs - Recent logs")

    # Run Flask app
    if is_production:
        # In production, this will be handled by Gunicorn via Procfile
        # But we keep this for fallback
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False
        )
    else:
        # Development mode
        app.run(
            host='0.0.0.0',
            port=port,
            debug=True
        )
