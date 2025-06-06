#!/usr/bin/env python3
"""
Enhanced Instagram Automation with Multiple Content Sources
This version uses hybrid approach: user uploads + curated content + AI generation + viral reels
"""

import os
import sys
import json
import time
import random
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Union
from instagrapi import Client
import requests
from PIL import Image, ImageDraw, ImageFont
import google.generativeai as genai
from dotenv import load_dotenv
# Load environment variables
load_dotenv()


class EnhancedInstagramAutomation:
    def __init__(self):
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(
                    'enhanced_automation.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Configuration
        self.username = os.getenv('INSTAGRAM_USERNAME')
        self.password = os.getenv('INSTAGRAM_PASSWORD')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.testing_mode = os.getenv('TESTING_MODE', 'True').lower() == 'true'

        # Setup directories
        self.content_dir = Path('user_content')
        self.downloads_dir = Path('downloads')
        self.posted_dir = Path('posted')
        self.generated_dir = Path('generated_content')

        for directory in [self.content_dir, self.downloads_dir, self.posted_dir, self.generated_dir]:
            directory.mkdir(exist_ok=True)
            (directory / 'images').mkdir(exist_ok=True)
            (directory / 'videos').mkdir(exist_ok=True)        # Initialize APIs
        self.client = Client()
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            # Try newer model first, fallback to older if needed
            try:
                self.ai_model = genai.GenerativeModel('gemini-1.5-flash')
            except:
                try:
                    self.ai_model = genai.GenerativeModel('gemini-1.5-pro')
                except:
                    self.ai_model = genai.GenerativeModel('gemini-pro')
        else:
            self.ai_model = None

        # Content tracking
        self.posted_content_file = 'posted_content.json'
        self.posted_content = self.load_posted_content()
        # Downloaded content tracking to avoid duplicates
        self.downloaded_content_file = 'downloaded_content.json'
        self.downloaded_content = self.load_downloaded_content()
        # Initialize next upload tracking for logging
        self.next_upload_times = []

        self.logger.info("Enhanced Instagram Automation initialized")

    def scan_user_content(self) -> List[str]:
        """Scan user_content directory for images and videos"""
        content_files = []
        # Scan for images
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        for ext in image_extensions:
            content_files.extend(list(self.content_dir.glob(f'**/*{ext}')))
            content_files.extend(list(self.content_dir.glob(
                f'**/*{ext.upper()}')))        # Scan for videos
        video_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
        for ext in video_extensions:
            content_files.extend(list(self.content_dir.glob(f'**/*{ext}')))
            content_files.extend(
                list(self.content_dir.glob(f'**/*{ext.upper()}')))

        return [str(f) for f in content_files]

    def generate_ai_caption(self, content_type: str, image_path: Optional[str] = None) -> str:
        """Generate AI caption with context"""
        try:
            prompt = "Create a cute and engaging Instagram caption for a cat photo/video. Include relevant hashtags like #catsofinstagram #cute #kitty #meow"

            if self.ai_model:
                response = self.ai_model.generate_content(prompt)
                return response.text
            else:
                return self.fallback_caption(content_type)

        except Exception as e:
            self.logger.warning(f"AI caption generation failed: {e}")
            return self.fallback_caption(content_type)

    def fallback_caption(self, content_type: str) -> str:
        """Fallback caption generation"""
        captions = [
            "😻 Adorable cat moment! 🐾\n\n#catsofinstagram #cute #kitty #meow #catlife #feline #pets",
            "🐱 This little furball has my heart! ❤️\n\n#cats #cute #kitty #catlovers #feline #pets #adorable",
            "😸 Purrfection captured! 📸\n\n#catsofinstagram #cats #kitty #cute #catlife #feline #meow"]
        return random.choice(captions)

    def fetch_viral_cat_reels_optimized(self, max_downloads: int = 1) -> List[str]:
        """Optimized algorithm to fetch viral cat reels using ONLY hashtag strategy - no account fetching"""
        downloaded_videos = []
        start_time = time.time()
        timeout_minutes = 3  # Reduced timeout to prevent hanging

        try:
            # Cat-related hashtags for finding viral reels
            cat_hashtags = [
                'cat', 'cats', 'kitty', 'kitten', 'meow',
                'catlife', "CatVideo",
                'FunnyCats', 'ViralCat', 'CuteCats', 'CatCompilation',
                'CatLovers', 'CatsOfInstagram', 'CatLife', 'Meow',
                'KittensOfTikTok', 'CatReels', 'CatViral', 'CatVideos',
                'CatFails', 'CatMemes', 'CatHumor'
            ]

            self.logger.info(
                f"🎬 Searching for up to {max_downloads} viral cat reels using HASHTAG STRATEGY ONLY...")

            # Login to Instagram for better access
            if not self.client.user_id:
                self.login_instagram()

            # ONLY Strategy: Search recent hashtag media (most reliable)
            # Try more hashtags                # Check timeout
            for hashtag in random.sample(cat_hashtags, min(5, len(cat_hashtags))):
                if time.time() - start_time > timeout_minutes * 60:
                    self.logger.warning(
                        "⏰ Timeout reached while fetching viral reels")
                    break

                if len(downloaded_videos) >= max_downloads:
                    self.logger.info(
                        f"✅ Target reached: {len(downloaded_videos)} videos downloaded")
                    break

                try:
                    self.logger.info(f"Searching hashtag: #{hashtag}")

                    # Get top media from hashtag (smaller batch for faster results)
                    medias = self.client.hashtag_medias_top(hashtag, amount=15)
                    self.logger.info(
                        f"📥 Fetched {len(medias)} media items from #{hashtag}")

                    # Debug: Log media types
                    video_count = sum(1 for m in medias if m.media_type == 2)
                    image_count = sum(1 for m in medias if m.media_type == 1)
                    self.logger.info(
                        f"📊 Media breakdown: {video_count} videos, {image_count} images")

                    # Filter for videos/reels with good engagement
                    video_candidates = []
                    for media in medias:
                        # Check timeout during processing
                        if time.time() - start_time > timeout_minutes * 60:
                            self.logger.warning(
                                "⏰ Timeout reached during media processing")
                            break

                        # Enhanced duplicate checking - multiple layers
                        if self.is_video_already_downloaded(str(media.pk)):
                            self.logger.debug(
                                f"🔍 Skipping duplicate: {media.pk}")
                            continue

                        # Basic video filtering - more lenient criteria
                        if media.media_type == 2:  # Video type
                            # More lenient engagement thresholds
                            like_count = media.like_count or 0
                            comment_count = media.comment_count or 0

                            # Lower thresholds for better content discovery
                            if like_count >= 1000 or comment_count >= 20:  # Much more lenient

                                # Check for cat content (but don't require it for hashtag-based search)
                                has_cat_content = True  # Assume cat content since we're searching cat hashtags
                                if media.caption_text:
                                    cat_words = [
                                        'cat', 'kitten', 'kitty', 'meow', 'feline', 'paw', 'purr', 'whiskers']
                                    has_cat_content = any(
                                        word in media.caption_text.lower() for word in cat_words)

                                # Include all videos from cat hashtags (since we're already filtering by hashtag)
                                video_candidates.append({
                                    'media': media,
                                    'score': like_count + (comment_count * 10),
                                    'has_cat_content': has_cat_content
                                })
                                self.logger.debug(
                                    f"✅ Added candidate: {media.pk} (likes: {like_count}, comments: {comment_count})")

                    # Sort by engagement score
                    video_candidates.sort(
                        key=lambda x: x['score'], reverse=True)
                    self.logger.info(
                        f"Found {len(video_candidates)} candidates from #{hashtag}")

                    # Download videos one by one for immediate posting
                    videos_downloaded_this_hashtag = 0  # Track downloads per hashtag
                    # Limit to top 2 per hashtag
                    for candidate in video_candidates[:2]:
                        # Check timeout before each download
                        if time.time() - start_time > timeout_minutes * 60:
                            self.logger.warning(
                                "⏰ Timeout reached before download")
                            break

                        # Fix: Strict adherence to max_downloads limit
                        if len(downloaded_videos) >= max_downloads:
                            self.logger.info(
                                f"✅ Reached max downloads limit ({max_downloads})")
                            break

                        media = candidate['media']

                        # Fix: Double-check for duplicates before downloading
                        if self.is_video_already_downloaded(str(media.pk)):
                            self.logger.info(
                                f"🔍 Skipping duplicate video: {media.pk}")
                            continue

                        self.logger.info(
                            f"Attempting download: {media.pk} (likes: {media.like_count})")

                        video_path = self.download_instagram_video(media)
                        if video_path:
                            downloaded_videos.append(video_path)
                            videos_downloaded_this_hashtag += 1
                            self.logger.info(
                                f"✅ Downloaded viral reel: {media.pk}")

                            # Return immediately if we have reached the limit
                            if len(downloaded_videos) >= max_downloads:
                                self.logger.info(
                                    f"🚀 Reached download limit ({max_downloads}) - ready for posting!")
                                break

                            time.sleep(2)  # Rate limiting between downloads
                      # Break out of hashtag loop if we've reached our limit
                    if len(downloaded_videos) >= max_downloads:
                        break
                    time.sleep(3)  # Hashtag rate limiting

                except Exception as e:
                    error_msg = str(e).lower()
                    if 'rate limit' in error_msg or 'too many requests' in error_msg or '429' in error_msg:
                        self.logger.warning(
                            f"🚫 Rate limit hit for hashtag #{hashtag}: {e}")
                        # Use enhanced rate limit handler
                        if not self.enhanced_rate_limit_handler(hashtag):
                            continue
                    elif 'login' in error_msg or 'authentication' in error_msg:
                        self.logger.error(
                            f"🔐 Authentication error for hashtag #{hashtag}: {e}")
                        self.logger.info("🔄 Attempting to re-login...")
                        if not self.login_instagram():
                            self.logger.error(
                                "❌ Re-login failed - stopping fetch routine")
                            break
                    else:
                        self.logger.warning(
                            f"⚠️ Error searching hashtag #{hashtag}: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Error in optimized viral reel fetching: {e}")

        elapsed_time = time.time() - start_time
        self.logger.info(
            f"🎬 Downloaded {len(downloaded_videos)} viral cat reels using hashtag strategy (took {elapsed_time:.1f}s)")

        if elapsed_time > timeout_minutes * 60:
            self.logger.warning(
                f"⏰ Fetch operation timed out after {timeout_minutes} minutes")

        return downloaded_videos

    def download_instagram_video(self, media) -> Optional[str]:
        """Download a specific Instagram video/reel with enhanced error handling and corruption prevention"""
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"viral_reel_{media.pk}_{timestamp}.mp4"
            filepath = self.downloads_dir / 'videos' / filename

            # Enhanced download with retry logic and validation
            max_download_attempts = 3
            expected_file_size = None

            for attempt in range(max_download_attempts):
                downloaded_file = None  # Initialize to prevent unbound variable
                try:
                    self.logger.info(
                        f"📥 Download attempt {attempt + 1}/{max_download_attempts} for video {media.pk}")

                    # Download the video using instagrapi's built-in method
                    video_path = self.client.video_download(
                        media.pk, folder=self.downloads_dir / 'videos')
                    downloaded_file = Path(video_path)

                    # Enhanced file validation
                    if not downloaded_file.exists():
                        raise Exception(
                            f"Downloaded file does not exist: {downloaded_file}")

                    file_size = downloaded_file.stat().st_size
                    self.logger.info(
                        f"Downloaded file size: {file_size:,} bytes")

                    # More robust size validation
                    min_size = 50 * 1024  # 50KB minimum for any video
                    max_size = 100 * 1024 * 1024  # 100MB maximum

                    if file_size < min_size:
                        raise Exception(
                            f"Downloaded file too small ({file_size:,} bytes), likely corrupted or incomplete")

                    if file_size > max_size:
                        self.logger.warning(
                            f"Large file detected ({file_size:,} bytes), proceeding with caution")

                    # Enhanced file integrity check
                    try:
                        with open(downloaded_file, 'rb') as f:
                            # Read and validate file header for MP4
                            header = f.read(12)
                            if len(header) < 12:
                                raise Exception(
                                    "File header too short, file appears incomplete")

                            # Check for common MP4 signatures
                            if not (b'ftyp' in header or b'moov' in header):
                                # Try reading more of the file to find MP4 signature
                                f.seek(0)
                                chunk = f.read(1024)
                                if b'ftyp' not in chunk and b'moov' not in chunk:
                                    raise Exception(
                                        "File does not appear to be a valid MP4 video")

                            # Verify we can read the entire file
                            f.seek(0, 2)  # Seek to end
                            actual_size = f.tell()
                            if actual_size != file_size:
                                raise Exception(
                                    f"File size mismatch: expected {file_size}, got {actual_size}")

                    except Exception as validation_error:
                        raise Exception(
                            f"File validation failed: {validation_error}")

                    # Consistency check for multiple attempts
                    if expected_file_size is None:
                        expected_file_size = file_size
                    elif abs(file_size - expected_file_size) > 1024:  # Allow 1KB tolerance
                        self.logger.warning(
                            f"File size inconsistency detected: expected ~{expected_file_size:,}, got {file_size:,}")

                    # Rename to our naming convention
                    final_path = filepath
                    downloaded_file.rename(final_path)

                    self.logger.info(
                        f"✅ Successfully downloaded and validated video: {filename} ({file_size:,} bytes)")

                    # Perform final validation on renamed file
                    if not final_path.exists() or final_path.stat().st_size != file_size:
                        raise Exception(
                            "File corrupted during rename operation")

                    break

                except Exception as download_error:
                    self.logger.warning(
                        f"⚠️ Download attempt {attempt + 1} failed: {download_error}")

                    # Clean up any partial files
                    # Always include the target filepath
                    cleanup_paths = [filepath]
                    if downloaded_file and downloaded_file.exists():
                        cleanup_paths.append(downloaded_file)

                    for cleanup_path in cleanup_paths:
                        try:
                            if cleanup_path.exists():
                                cleanup_path.unlink()
                                self.logger.info(
                                    f"🧹 Cleaned up partial file: {cleanup_path.name}")
                        except Exception as cleanup_error:
                            self.logger.warning(
                                f"Failed to cleanup {cleanup_path}: {cleanup_error}")

                    if attempt == max_download_attempts - 1:
                        raise Exception(
                            f"All {max_download_attempts} download attempts failed")

                    # Progressive retry delay with exponential backoff
                    # 5s, 10s, 20s (max 30s)
                    retry_delay = min(5 * (2 ** attempt), 30)
                    self.logger.info(
                        f"⏳ Waiting {retry_delay}s before retry...")
                    time.sleep(retry_delay)

            else:
                raise Exception("Download loop completed without success")

            # Save enhanced metadata for caption generation and tracking
            metadata = {
                'media_id': str(media.pk),
                'original_caption': media.caption_text,
                'like_count': media.like_count,
                'comment_count': media.comment_count,
                'username': media.user.username,
                'download_date': datetime.now().isoformat(),
                'file_size_bytes': final_path.stat().st_size,
                'download_attempts': attempt + 1,
                'hashtags': self.extract_hashtags(media.caption_text),
                'validation_passed': True
            }

            metadata_file = final_path.with_suffix('.json')
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            # Track downloaded video to avoid duplicates
            self.track_downloaded_video(media.pk)

            self.logger.info(
                f"📥 Successfully downloaded and tracked video: {filename}")
            return str(final_path)

        except Exception as e:
            self.logger.error(f"❌ Error downloading video {media.pk}: {e}")

            # Cleanup any remaining files on final failure
            try:
                # Generate the same filepath for cleanup
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                cleanup_filepath = self.downloads_dir / 'videos' / \
                    f"viral_reel_{media.pk}_{timestamp}.mp4"

                cleanup_patterns = [cleanup_filepath,
                                    cleanup_filepath.with_suffix('.json')]
                for cleanup_pattern in cleanup_patterns:
                    if cleanup_pattern.exists():
                        cleanup_pattern.unlink()
                        self.logger.info(
                            f"🧹 Cleaned up failed download: {cleanup_pattern.name}")
            except Exception as cleanup_error:
                self.logger.warning(f"Failed final cleanup: {cleanup_error}")

            return None

    def extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        if not text:
            return []
        hashtags = re.findall(r'#\w+', text.lower())
        return [tag[1:] for tag in hashtags]  # Remove # symbol

    def generate_video_caption(self, video_path: Optional[str] = None) -> str:
        """Generate AI caption specifically for video content"""
        try:
            # Load metadata if available
            metadata = None
            if video_path:
                metadata_file = Path(video_path).with_suffix('.json')
                if metadata_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)

            # Create video-specific prompt
            if metadata and metadata.get('original_caption'):
                # Limit length
                original_caption = metadata['original_caption'][:200]
                prompt = f"""Create a fresh, engaging Instagram reel caption inspired by this viral cat content: "{original_caption}"
                
                Requirements:
                - Make it original and unique (don't copy)
                - Focus on cat behavior, cuteness, or humor
                - Include 5-8 relevant hashtags
                - Keep it under 150 characters for reels
                - Make it shareable and engaging"""
            else:
                prompt = """Create a viral Instagram reel caption for a cute cat video.
                
                Requirements:
                - Focus on cat cuteness, funny behavior, or relatable moments
                - Include trending cat hashtags
                - Keep it short and punchy for reels
                - Make it shareable and engaging
                - Under 150 characters"""

            if self.ai_model:
                response = self.ai_model.generate_content(prompt)
                caption = response.text.strip()

                # Ensure hashtags are included
                if '#' not in caption:
                    caption += "\n\n#catsofinstagram #cutecat #funnycats #reels #viral"

                return caption
            else:
                return self.fallback_video_caption()

        except Exception as e:
            self.logger.warning(f"AI video caption generation failed: {e}")
            return self.fallback_video_caption()

    def fallback_video_caption(self) -> str:
        """Fallback caption for videos"""
        video_captions = [
            "🎬 This cat is pure entertainment! 😹\n\n#catsofinstagram #funnycats #reels #viral #cutecats",
            "😻 Can't stop watching this! 🔄\n\n#catreel #funnypets #catsofinstagram #viral #cute",
            "🐱 When cats are this adorable... 💕\n\n#cutecats #catsofinstagram #reels #adorable #pets",
            "😸 This made my day! 🌟\n\n#happycats #funnycats #catsofinstagram #viral #joy",
            "🎥 Cat content that hits different! ✨\n\n#catvideo #funnypets #catsofinstagram #trending"
        ]
        return random.choice(video_captions)

    def post_content(self, file_path: Union[str, Path], caption: str) -> bool:
        """Post content to Instagram with timeout protection"""
        if self.testing_mode:
            self.logger.info(f"[TESTING MODE] Would post: {file_path}")
            # Clean caption for logging to avoid Unicode issues
            clean_caption = caption.encode('ascii', 'ignore').decode('ascii')
            self.logger.info(
                f"[TESTING MODE] Caption: {clean_caption[:100]}...")
            return True

        try:
            # Login if needed with timeout protection
            if not self.client.user_id:
                self.logger.info("Logging into Instagram for posting...")
                login_success = self.login_instagram()
                if not login_success:
                    self.logger.error("Failed to login - cannot post content")
                    return False

            file_path_obj = Path(file_path)

            # Add timeout protection for uploads
            upload_timeout = 120  # 2 minutes max for upload
            start_time = time.time()

            if file_path_obj.suffix.lower() in ['.mp4', '.mov', '.avi', '.mkv', '.webm']:
                # Post video as reel for better engagement
                try:
                    self.logger.info(f"Uploading reel: {file_path_obj.name}")
                    # Try posting as reel first (better for viral content)
                    self.client.clip_upload(file_path_obj, caption)
                    self.logger.info(f"Posted reel: {file_path_obj.name}")
                except Exception as reel_error:
                    # Check if we exceeded timeout
                    if time.time() - start_time > upload_timeout:
                        self.logger.error(
                            f"Upload timed out after {upload_timeout}s")
                        return False

                    self.logger.warning(
                        f"Reel upload failed, trying regular video: {reel_error}")
                    try:
                        # Fallback to regular video upload
                        self.client.video_upload(file_path_obj, caption)
                        self.logger.info(f"Posted video: {file_path_obj.name}")
                    except Exception as video_error:
                        self.logger.error(
                            f"Both reel and video upload failed: {video_error}")
                        return False
            else:
                # Post image
                try:
                    self.client.photo_upload(file_path_obj, caption)
                    self.logger.info(f"Posted image: {file_path_obj.name}")
                except Exception as photo_error:
                    self.logger.error(f"Photo upload failed: {photo_error}")
                    return False

            # Track posted content
            content_type = 'images' if file_path_obj.suffix.lower(
            ) in ['.jpg', '.jpeg', '.png', '.gif'] else 'videos'
            self.posted_content[content_type].append({
                'file': str(file_path_obj),
                'caption': caption,
                'posted_at': datetime.now().isoformat(),
                'source': 'enhanced_automation'
            })
            self.save_posted_content()

            return True

        except Exception as e:
            self.logger.error(f"Error posting content: {e}")
            return False

    def login_instagram(self) -> bool:
        """Login to Instagram with timeout protection"""
        try:
            self.logger.info("Attempting Instagram login...")
            login_start = time.time()
            login_timeout = 30  # 30 seconds max for login

            # Set a shorter timeout for the login process
            self.client.login(self.username, self.password)

            login_time = time.time() - login_start
            if login_time > login_timeout:
                self.logger.warning(
                    f"Login took {login_time:.1f}s (longer than expected)")

            self.logger.info("Successfully logged into Instagram")
            return True

        except Exception as e:
            self.logger.error(f"Instagram login failed: {e}")
            return False

    def load_posted_content(self) -> Dict:
        """Load posted content tracking"""
        if os.path.exists(self.posted_content_file):
            try:
                with open(self.posted_content_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {'images': [], 'videos': []}

    def save_posted_content(self):
        """Save posted content tracking"""
        with open(self.posted_content_file, 'w') as f:
            json.dump(self.posted_content, f, indent=2)

    def load_downloaded_content(self) -> Dict:
        """Load downloaded content tracking"""
        if os.path.exists(self.downloaded_content_file):
            try:
                with open(self.downloaded_content_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {'video_ids': [], 'last_cleanup': None}

    def save_downloaded_content(self):
        """Save downloaded content tracking"""
        with open(self.downloaded_content_file, 'w') as f:
            json.dump(self.downloaded_content, f, indent=2)

    def is_video_already_downloaded(self, media_pk: str, username: Optional[str] = None) -> bool:
        """Enhanced duplicate checking - multiple layers of verification"""
        try:
            media_pk_str = str(media_pk)

            # Layer 1: Check video ID tracking with better logging
            if media_pk_str in self.downloaded_content.get('video_ids', []):
                self.logger.info(
                    f"🔍 Video {media_pk} already tracked as downloaded (Layer 1)")
                return True

            # Layer 2: Check if file already exists in downloads folder (more thorough)
            downloads_video_dir = self.downloads_dir / 'videos'
            if downloads_video_dir.exists():
                # Check for any file containing the media_pk
                for video_file in downloads_video_dir.glob('*.mp4'):
                    if media_pk_str in video_file.name:
                        self.logger.info(
                            f"🔍 Video {media_pk} file already exists: {video_file.name} (Layer 2)")
                        # Add to tracking if not already there
                        if media_pk_str not in self.downloaded_content.get('video_ids', []):
                            self.track_downloaded_video(media_pk_str)
                        return True

            # Layer 3: Check metadata files (more thorough)
            if downloads_video_dir.exists():
                for metadata_file in downloads_video_dir.glob('*.json'):
                    if media_pk_str in metadata_file.name:
                        self.logger.info(
                            f"🔍 Video {media_pk} metadata already exists: {metadata_file.name} (Layer 3)")
                        # Add to tracking if not already there
                        if media_pk_str not in self.downloaded_content.get('video_ids', []):
                            self.track_downloaded_video(media_pk_str)
                        return True

            # Layer 4: Check posted content to avoid re-downloading already posted videos
            for posted_video in self.posted_content.get('videos', []):
                posted_file = posted_video.get('file', '')
                if media_pk_str in posted_file:
                    self.logger.info(
                        f"🔍 Video {media_pk} already posted: {Path(posted_file).name} (Layer 4)")
                    # Add to tracking if not already there
                    if media_pk_str not in self.downloaded_content.get('video_ids', []):
                        self.track_downloaded_video(media_pk_str)
                    return True
              # Layer 5: Check if video_id is in any existing file names more broadly
            if downloads_video_dir.exists():
                for file_path in downloads_video_dir.iterdir():
                    if file_path.is_file() and media_pk_str in str(file_path.stem):
                        self.logger.info(
                            f"🔍 Video {media_pk} found in existing files: {file_path.name} (Layer 5)")
                        # Add to tracking if not already there
                        if media_pk_str not in self.downloaded_content.get('video_ids', []):
                            self.track_downloaded_video(media_pk_str)
                        return True

            # If we get here, it's truly a new video
            self.logger.debug(
                f"✅ Video {media_pk} is new and can be downloaded")
            return False

        except Exception as e:
            self.logger.warning(
                f"Error checking duplicate for {media_pk}: {e}")
            return False  # If we can't check, allow download but log the issue

    def track_downloaded_video(self, video_id: str):
        """Track a downloaded video to avoid duplicates"""
        if 'video_ids' not in self.downloaded_content:
            self.downloaded_content['video_ids'] = []
        if str(video_id) not in self.downloaded_content['video_ids']:
            self.downloaded_content['video_ids'].append(str(video_id))
            # Keep only last 1000 video IDs to prevent file from growing too large
            if len(self.downloaded_content['video_ids']) > 1000:
                self.downloaded_content['video_ids'] = self.downloaded_content['video_ids'][-1000:]
            self.save_downloaded_content()
            self.logger.info(f"🆔 Tracked downloaded video: {video_id}")
        else:
            self.logger.info(f"🆔 Video {video_id} already tracked")

    def enhanced_posting_routine(self):
        """Optimized posting routine - posts immediately when content is available"""
        self.logger.info("Starting optimized posting routine...")

        content_posted = 0
        # Configuration for testing vs production
        # Single post for testing, 2 for production
        target_posts = 1 if self.testing_mode else 2

        # Strategy 1: User uploaded content (highest priority)
        user_files = self.scan_user_content()
        if user_files and content_posted < target_posts:
            self.logger.info(f"Found {len(user_files)} user content files")
            for file_path in user_files[:target_posts - content_posted]:
                caption = self.generate_ai_caption('user_content', file_path)
                if self.post_content(file_path, caption):
                    content_posted += 1
                    # Use shorter delay in testing mode
                    delay = 5 if self.testing_mode else random.randint(
                        300, 600)
                    time.sleep(delay)

        # Strategy 2: Check existing downloaded videos first
        existing_videos = []
        downloads_video_dir = self.downloads_dir / 'videos'
        if downloads_video_dir.exists():
            existing_videos = [
                f for f in downloads_video_dir.glob('*.mp4') if f.is_file()]

        self.logger.info(
            f"Found {len(existing_videos)} existing downloaded videos")

        # Strategy 3: Always try to download new content first, then use existing as fallback
        if content_posted < target_posts:
            # STEP 1: Always try to download new viral content first with enhanced retry
            self.logger.info(
                "🎬 Attempting to fetch new viral cat reels with enhanced retry logic...")
            remaining_posts = target_posts - content_posted

            # Fix: Ensure we only download exactly what we need
            # Only download 1 at a time for better control
            max_downloads_needed = min(remaining_posts, 1)

            try:
                viral_reels = self.fetch_viral_cat_reels_with_retry(
                    max_downloads=max_downloads_needed, max_retries=3)

                if viral_reels:
                    self.logger.info(
                        f"✅ Successfully downloaded {len(viral_reels)} new viral reels")
                    for video_path in viral_reels:
                        if content_posted >= target_posts:
                            break

                        caption = self.generate_video_caption(video_path)
                        if self.post_content(video_path, caption):
                            # Fix: Always cleanup downloaded videos after posting (whether successful or not)
                            cleanup_success = self.cleanup_posted_viral_reel(
                                video_path)
                            if cleanup_success:
                                self.logger.info(
                                    f"🗑️ Successfully cleaned up: {Path(video_path).name}")
                            else:
                                self.logger.warning(
                                    f"⚠️ Failed to cleanup: {Path(video_path).name}")
                            content_posted += 1

                            if content_posted < target_posts:
                                delay = 10 if self.testing_mode else random.randint(
                                    600, 1200)
                                time.sleep(delay)
                        else:
                            # Fix: Even if posting fails, still cleanup the downloaded file
                            self.logger.warning(
                                f"❌ Posting failed for: {Path(video_path).name}, cleaning up anyway...")
                            self.cleanup_posted_viral_reel(video_path)
                else:
                    self.logger.warning(
                        "⚠️ No new viral reels could be downloaded (rate limit or error)")

            except Exception as e:
                self.logger.error(f"❌ Error fetching new viral reels: {e}")

            # STEP 2: Only use existing videos as fallback if we still need content AND they haven't been posted recently
            if content_posted < target_posts:
                # Filter existing videos to exclude recently posted ones
                unposted_existing_videos = self.filter_unposted_existing_videos(
                    existing_videos)

                if unposted_existing_videos:
                    self.logger.info(
                        f"📹 Using {len(unposted_existing_videos)} unposted existing videos as fallback...")
                    for video_path in unposted_existing_videos[:target_posts - content_posted]:
                        caption = self.generate_video_caption(str(video_path))
                        if self.post_content(str(video_path), caption):
                            # Fix: Cleanup existing videos after posting too
                            cleanup_success = self.cleanup_posted_viral_reel(
                                str(video_path))
                            if cleanup_success:
                                self.logger.info(
                                    f"🗑️ Successfully cleaned up existing video: {Path(video_path).name}")
                            content_posted += 1
                            if content_posted < target_posts:
                                delay = 10 if self.testing_mode else random.randint(
                                    600, 1200)
                                time.sleep(delay)
                        else:
                            # Fix: Cleanup even failed posts to prevent accumulation
                            self.logger.warning(
                                f"❌ Posting failed for existing video: {Path(video_path).name}, cleaning up anyway...")
                            self.cleanup_posted_viral_reel(str(video_path))
                else:
                    self.logger.warning(
                        "⚠️ No unposted existing videos available - skipping this routine")

        self.logger.info(f"Posted {content_posted} items in this routine")

    def setup_scheduler(self):
        """Setup posting schedule - REMOVED FOR CRON JOB DEPLOYMENT"""
        # This method is now disabled for external cron job scheduling
        self.logger.info(
            "📅 Scheduler disabled - using external cron job scheduling")

    def run_continuous_service(self):
        """Run as a continuous service - REMOVED FOR CRON JOB DEPLOYMENT"""
        # This method is now disabled for external cron job scheduling
        self.logger.info(
            "🚀 Continuous service disabled - using external cron job scheduling")

    def run(self):
        """Main run method - Modified for single execution"""
        self.logger.info(
            "Enhanced Instagram Automation started - Single execution mode")

        # Create user content directory with instructions
        self.create_user_instructions()

        # Run posting routine once and exit
        self.logger.info("🚀 Running posting routine...")
        self.enhanced_posting_routine()

        self.logger.info("✅ Posting routine completed - Exiting")

    def display_countdown_timer(self):
        """Display countdown timer - REMOVED FOR CRON JOB DEPLOYMENT"""
        # This method is now disabled for external cron job scheduling
        pass

    def update_next_upload_times(self):
        """Update next upload times - REMOVED FOR CRON JOB DEPLOYMENT"""
        # This method is now disabled for external cron job scheduling
        pass

    def log_remaining_time_to_upload(self):
        """Log remaining time - REMOVED FOR CRON JOB DEPLOYMENT"""
        # This method is now disabled for external cron job scheduling
        pass

    def start_time_logging_thread(self):
        """Start time logging thread - REMOVED FOR CRON JOB DEPLOYMENT"""
        # This method is now disabled for external cron job scheduling
        pass

    def enhanced_rate_limit_handler(self, hashtag: str, attempt: int = 1, max_attempts: int = 3) -> bool:
        """Enhanced rate limit handling with exponential backoff and different strategies"""
        try:
            base_delay = 30  # Base delay in seconds
            # Exponential backoff: 30s, 60s, 120s
            delay = base_delay * (2 ** (attempt - 1))

            self.logger.warning(
                f"🚫 Rate limit detected for #{hashtag} (attempt {attempt}/{max_attempts})")
            self.logger.info(
                f"⏳ Implementing enhanced backoff strategy: waiting {delay}s...")

            # For longer delays, log progress
            if delay > 60:
                for i in range(delay // 30):
                    time.sleep(30)
                    remaining = delay - (i + 1) * 30
                    if remaining > 0:
                        self.logger.info(
                            f"⏳ Rate limit cooldown: {remaining}s remaining...")
                time.sleep(delay % 30)  # Sleep remaining time
            else:
                time.sleep(delay)

            # Try to refresh authentication on repeated failures
            if attempt >= 2:
                self.logger.info(
                    "🔄 Refreshing authentication due to repeated rate limits...")
                if not self.login_instagram():
                    self.logger.error("❌ Authentication refresh failed")
                    return False

            return True

        except Exception as e:
            self.logger.error(f"Error in rate limit handler: {e}")
            return False

    def fetch_viral_cat_reels_with_retry(self, max_downloads: int = 1, max_retries: int = 3) -> List[str]:
        """Enhanced fetch with retry logic and better rate limit handling"""
        downloaded_videos = []

        for retry_attempt in range(max_retries):
            self.logger.info(
                f"🎬 Fetch attempt {retry_attempt + 1}/{max_retries}")

            try:
                # Use the existing optimized fetch method
                videos = self.fetch_viral_cat_reels_optimized(max_downloads)

                if videos:
                    downloaded_videos.extend(videos)
                    self.logger.info(
                        f"✅ Successfully downloaded {len(videos)} videos on attempt {retry_attempt + 1}")
                    break

                elif retry_attempt < max_retries - 1:
                    # Wait longer between full retry attempts
                    retry_delay = 60 * (retry_attempt + 1)  # 60s, 120s, 180s
                    self.logger.info(
                        f"⏳ No content found, waiting {retry_delay}s before retry...")
                    time.sleep(retry_delay)

            except Exception as e:
                error_msg = str(e).lower()
                if 'rate limit' in error_msg or 'too many requests' in error_msg:
                    if not self.enhanced_rate_limit_handler("fetch_retry", retry_attempt + 1, max_retries):
                        break
                else:
                    self.logger.error(
                        f"❌ Fetch error on attempt {retry_attempt + 1}: {e}")
                    if retry_attempt < max_retries - 1:
                        time.sleep(30)  # Wait before next attempt

        return downloaded_videos

    def cleanup_posted_viral_reel(self, video_path: str) -> bool:
        """Clean up downloaded viral reel files after successful posting with robust retry logic"""
        def safe_delete_file(file_path: Path, max_retries: int = 3) -> bool:
            """Safely delete a file with retries for Windows file locking issues"""
            if not file_path.exists():
                return True

            for attempt in range(max_retries):
                try:
                    file_path.unlink()
                    return True
                except PermissionError as e:
                    if "being used by another process" in str(e):
                        delay = (attempt + 1) * 2  # 2, 4, 6 seconds
                        self.logger.info(
                            f"File locked, waiting {delay}s before retry {attempt + 1}/{max_retries}")
                        time.sleep(delay)
                    else:
                        self.logger.warning(
                            f"Permission error deleting {file_path.name}: {e}")
                        return False
                except OSError as e:
                    self.logger.warning(
                        f"OS error deleting {file_path.name}: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                    else:
                        return False
                except Exception as e:
                    self.logger.warning(
                        f"Unexpected error deleting {file_path.name}: {e}")
                    return False

            self.logger.warning(
                f"Failed to delete {file_path.name} after {max_retries} attempts")
            return False

        cleanup_success = True
        try:
            video_file = Path(video_path)
            metadata_file = video_file.with_suffix('.json')
            # Fix thumbnail file path - it should be just .jpg, not .mp4.jpg
            thumbnail_file = video_file.parent / (video_file.stem + '.jpg')

            # Wait for Instagram API to release file handles
            time.sleep(2)

            # Delete the video file with retries
            if safe_delete_file(video_file):
                self.logger.info(
                    f"🗑️ Cleaned up video file: {video_file.name}")
            else:
                cleanup_success = False

            # Delete the metadata file
            if safe_delete_file(metadata_file):
                self.logger.info(
                    f"🗑️ Cleaned up metadata file: {metadata_file.name}")
            else:
                cleanup_success = False

            # Delete thumbnail if it exists
            if safe_delete_file(thumbnail_file):
                self.logger.info(
                    f"🗑️ Cleaned up thumbnail file: {thumbnail_file.name}")
            else:
                # Thumbnail deletion failure is not critical
                self.logger.info(
                    f"ℹ️ Thumbnail file may not exist or is locked: {thumbnail_file.name}")

        except Exception as e:
            self.logger.warning(f"Error in cleanup routine: {e}")
            cleanup_success = False

        return cleanup_success

    def filter_unposted_existing_videos(self, existing_videos: List) -> List:
        """Filter existing videos to exclude ones that have been posted recently"""
        try:
            unposted_videos = []
            posted_videos = self.posted_content.get('videos', [])

            # Get list of recently posted video file names (last 7 days)
            cutoff_date = datetime.now() - timedelta(days=7)
            recent_posted_files = set()

            for posted_video in posted_videos:
                posted_at_str = posted_video.get('posted_at', '')
                try:
                    posted_at = datetime.fromisoformat(
                        posted_at_str.replace('Z', '+00:00'))
                    if posted_at > cutoff_date:
                        # Extract just the filename from the full path
                        posted_file = Path(posted_video.get('file', '')).name
                        recent_posted_files.add(posted_file)
                except Exception:
                    # If we can't parse the date, assume it's recent to be safe
                    posted_file = Path(posted_video.get('file', '')).name
                    recent_posted_files.add(posted_file)

            # Filter existing videos
            for video_path in existing_videos:
                video_filename = Path(video_path).name
                if video_filename not in recent_posted_files:
                    unposted_videos.append(video_path)
                else:
                    self.logger.info(
                        f"🚫 Skipping recently posted video: {video_filename}")

            self.logger.info(
                f"📊 Found {len(unposted_videos)} unposted videos out of {len(existing_videos)} existing videos")
            return unposted_videos

        except Exception as e:
            self.logger.error(f"Error filtering unposted videos: {e}")
            # If filtering fails, return all existing videos to avoid complete failure
            return existing_videos

    def create_user_instructions(self):
        """Create instructions for user content"""
        instructions_file = self.content_dir / 'HOW_TO_USE.txt'
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write("""
INSTAGRAM AUTOMATION - USER CONTENT GUIDE (CRON JOB MODE)
==========================================================

PLACE YOUR CONTENT HERE:

1. DROP CAT IMAGES/VIDEOS:
   - Place any cat photos (.jpg, .png, .gif) in this folder
   - Place any cat videos (.mp4, .mov) in this folder
   - The system will automatically post them with AI-generated captions

2. CONTENT SOURCES (Priority Order):
   Priority 1: Your uploaded files (this folder) - HIGHEST PRIORITY
   Priority 2: 🎬 VIRAL CAT REELS - Downloaded and posted IMMEDIATELY

3. CRON JOB MODE:
   ✅ Script runs once per execution (no internal scheduling)
   ✅ Designed for external cron job scheduling (e.g., Render Cron Jobs)
   ✅ Downloads one video at a time for fastest posting
   ✅ Automatically cleans up downloaded viral reel files after posting
   ✅ AI generates fresh captions (never copies original captions)
   ✅ Respects rate limits and Instagram ToS

4. RECOMMENDED CRON SCHEDULE:
   - 9:00 AM - Morning post
   - 3:00 PM - Afternoon post  
   - 8:00 PM - Evening post
   (Total: 3 posts per day - Instagram-friendly frequency)
   
   Example cron expressions:
   - 0 9 * * * (9 AM daily)
   - 0 15 * * * (3 PM daily)
   - 0 20 * * * (8 PM daily)

5. EXECUTION MODE:
   - Each run processes one posting routine and exits
   - No continuous loops or internal scheduling
   - Perfect for external cron job systems
   - Runs immediately when called

6. AI CAPTIONS:
   - Each post gets a unique AI-generated caption
   - Video captions optimized for reels
   - Includes trending hashtags automatically
   - Fallback captions if AI fails

7. TESTING MODE:
   - Set TESTING_MODE=True (check .env file) to test without posting
   - Run 'python enhanced_automation.py test' for testing

8. AUTOMATIC CLEANUP:
   - Downloaded viral reels are automatically deleted after posting
   - Keeps your storage clean and organized
   - Metadata files are also cleaned up
   - Robust retry logic for Windows file locking

ENJOY YOUR OPTIMIZED VIRAL CAT CONTENT WITH CRON JOB SCHEDULING! 🐱🚀✨
""")

        self.logger.info(f"Created user instructions: {instructions_file}")

    def cleanup_old_downloads(self, days_old: int = 7):
        """Clean up old downloaded videos and tracking data"""
        try:
            downloads_video_dir = self.downloads_dir / 'videos'
            if not downloads_video_dir.exists():
                return

            cutoff_date = datetime.now() - timedelta(days=days_old)
            cleaned_files = 0

            # Clean up old video files
            for video_file in downloads_video_dir.glob('*.mp4'):
                try:
                    file_date = datetime.fromtimestamp(
                        video_file.stat().st_mtime)
                    if file_date < cutoff_date:
                        # Also remove associated metadata file
                        metadata_file = video_file.with_suffix('.json')
                        if metadata_file.exists():
                            metadata_file.unlink()

                        video_file.unlink()
                        cleaned_files += 1
                        self.logger.info(
                            f"🧹 Cleaned up old file: {video_file.name}")
                except Exception as e:
                    self.logger.warning(
                        f"Error removing old file {video_file}: {e}")
              # Update tracking data cleanup timestamp
            self.downloaded_content['last_cleanup'] = datetime.now(
            ).isoformat()
            self.save_downloaded_content()

            self.logger.info(
                f"🧹 Cleanup complete: removed {cleaned_files} old files")

        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")


if __name__ == "__main__":
    automation = EnhancedInstagramAutomation()

    if len(sys.argv) > 1:
        if sys.argv[1] == 'test':
            # Run single test posting routine
            automation.enhanced_posting_routine()
        else:
            print("Usage: python enhanced_automation.py [test]")
            print("  test    - Run one posting routine and exit")
            print("  (no args) - Run one posting routine and exit")
    else:
        # Default behavior: run once and exit (for cron job)
        automation.run()
