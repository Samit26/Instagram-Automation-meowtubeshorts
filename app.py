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
            automation_instance = EnhancedInstagramAutomation()
            logger.info("✅ Automation instance created successfully")
        except Exception as e:
            logger.error(f"❌ Failed to create automation instance: {e}")
            raise
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
            '/status': 'Get service status'
        }
    })


@app.route('/run-task', methods=['GET', 'POST'])
def run_task():
    """Execute the Instagram automation task"""
    start_time = datetime.now()
    logger.info(f"🚀 Task execution requested at {start_time.isoformat()}")

    try:
        # Get automation instance
        automation = get_automation_instance()

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

    # Production configuration for Render
    logger.info(f"🚀 Starting Instagram Automation Flask Server on port {port}")
    logger.info(f"📱 Service endpoints available:")
    logger.info(f"   GET  / - Health check")
    logger.info(f"   GET/POST /run-task - Execute automation")
    logger.info(f"   GET  /status - Service status")
    logger.info(f"   GET  /logs - Recent logs")

    # Run Flask app
    app.run(
        host='0.0.0.0',  # Required for Render
        port=port,
        debug=False  # Set to False for production
    )
