# YouTube Video Downloader - Flask Application

A Flask web application to download YouTube videos using pytubefix (without yt-dlp), designed to run on Render.com.

## Features

- Download YouTube videos in various quality options
- Get video information (title, author, duration, views)
- Real-time progress bar during download
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

Or for production (using gunicorn):
```bash
gunicorn app:app --bind 0.0.0.0:5000
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
     - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
     - **Environment**: Python 3

3. The application will be automatically deployed

### Start Command for Render.com

When setting up manually on Render.com, use this start command:

```
gunicorn app:app --bind 0.0.0.0:$PORT
```

This command:
- Uses `gunicorn` (production WSGI server)
- `app:app` refers to the `app` variable in `app.py`
- `--bind 0.0.0.0:$PORT` binds to all interfaces on Render's PORT

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

### POST `/api/download`
Start a video download (returns download_id for progress tracking).

**Body:**
```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID",
  "quality": "720p"
}
```

### GET `/api/progress/<download_id>`
Get download progress.

**Response:**
```json
{
  "success": true,
  "progress": 75.5,
  "status": "downloading"
}
```

### GET `/api/download/<download_id>/file`
Download the completed video file.

## Important Notes

⚠️ **Legal Notice**: Downloading YouTube videos may violate YouTube's Terms of Service. This application is for educational purposes. Please respect copyright laws and YouTube's terms.

## Requirements

- Python 3.7+
- Flask 3.0.0
- pytubefix 10.3.6 (fixed fork of pytube)
- gunicorn 21.2.0 (for production deployment)

## License

This project is for educational purposes only.
