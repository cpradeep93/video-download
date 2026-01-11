# YouTube Video Downloader - Flask Application

A Flask web application to download YouTube videos using pytube (without yt-dlp), designed to run on Render.com.

## Features

- Download YouTube videos in various quality options
- Get video information (title, author, duration, views)
- Simple web interface
- REST API endpoints
- Ready for Render.com deployment

## Local Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python app.py
```

3. Open your browser and navigate to `http://localhost:5000`

## Deployment to Render.com

1. Push your code to a GitHub repository

2. In Render.com dashboard:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect the settings from `render.yaml`
   - Or manually configure:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `python app.py`
     - **Environment**: Python 3

3. The application will be automatically deployed

## API Endpoints

### GET `/api/info`
Get video information without downloading.

**Parameters:**
- `url` (required): YouTube video URL

**Example:**
```
GET /api/info?url=https://www.youtube.com/watch?v=VIDEO_ID
```

**Response:**
```json
{
  "success": true,
  "video": {
    "title": "Video Title",
    "author": "Channel Name",
    "length": 120,
    "views": 1000000,
    "thumbnail": "https://...",
    "available_streams": [...]
  }
}
```

### GET `/api/download`
Download a YouTube video.

**Parameters:**
- `url` (required): YouTube video URL
- `quality` (optional): Video quality (`highest`, `lowest`, `720p`, `480p`, etc.)
- `itag` (optional): Specific stream itag

**Example:**
```
GET /api/download?url=https://www.youtube.com/watch?v=VIDEO_ID&quality=720p
```

## Important Notes

⚠️ **Legal Notice**: Downloading YouTube videos may violate YouTube's Terms of Service. This application is for educational purposes. Please respect copyright laws and YouTube's terms.

## Requirements

- Python 3.7+
- Flask 3.0.0
- pytube 15.0.0

## License

This project is for educational purposes only.
