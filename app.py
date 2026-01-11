from flask import Flask, request, jsonify, send_file, Response
from pytubefix import YouTube
import os
import tempfile
import logging
import threading
import time
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# Configure temporary directory for downloads
DOWNLOAD_DIR = tempfile.gettempdir()

# Store download progress (in production, use Redis or database)
download_progress = {}
download_files = {}  # Store filepath with download_id
progress_lock = threading.Lock()


def update_progress(download_id, progress, status='downloading', filepath=None):
    """Update download progress"""
    with progress_lock:
        download_progress[download_id] = {
            'progress': progress,
            'status': status,
            'timestamp': time.time()
        }
        if filepath:
            download_files[download_id] = filepath


def get_video_info(url):
    """Get video information without downloading"""
    try:
        yt = YouTube(url)
        streams = yt.streams.filter(progressive=True, file_extension='mp4')
        
        video_info = {
            'title': yt.title,
            'author': yt.author,
            'length': yt.length,
            'views': yt.views,
            'thumbnail': yt.thumbnail_url,
            'available_streams': []
        }
        
        for stream in streams.order_by('resolution').desc():
            video_info['available_streams'].append({
                'itag': stream.itag,
                'resolution': stream.resolution,
                'fps': stream.fps,
                'filesize': stream.filesize,
                'mime_type': stream.mime_type
            })
        
        return video_info, None
    except Exception as e:
        return None, str(e)


def on_progress_callback(stream, chunk, bytes_remaining, download_id):
    """Callback function for download progress"""
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    progress = (bytes_downloaded / total_size) * 100 if total_size > 0 else 0
    update_progress(download_id, progress, 'downloading')


def download_video(url, download_id, itag=None, quality='highest'):
    """Download YouTube video with progress tracking"""
    try:
        update_progress(download_id, 0, 'initializing')
        
        # Create progress callback
        def progress_callback(stream, chunk, bytes_remaining):
            on_progress_callback(stream, chunk, bytes_remaining, download_id)
        
        yt = YouTube(url, on_progress_callback=progress_callback)
        
        update_progress(download_id, 5, 'fetching_streams')
        
        if itag:
            stream = yt.streams.get_by_itag(itag)
        elif quality == 'highest':
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        elif quality == 'lowest':
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').asc().first()
        else:
            stream = yt.streams.filter(progressive=True, file_extension='mp4', resolution=quality).first()
        
        if not stream:
            update_progress(download_id, 0, 'error')
            return None, "No suitable stream found"
        
        update_progress(download_id, 10, 'downloading')
        
        # Download to temporary file
        filename = secure_filename(yt.title) + '.mp4'
        filepath = os.path.join(DOWNLOAD_DIR, filename)
        stream.download(output_path=DOWNLOAD_DIR, filename=filename)
        
        update_progress(download_id, 100, 'completed', filepath)
        return filepath, None
    except Exception as e:
        update_progress(download_id, 0, 'error')
        return None, str(e)


@app.route('/')
def index():
    """Home page"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>YouTube Video Downloader</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
            }
            .form-group {
                margin: 20px 0;
            }
            label {
                display: block;
                margin-bottom: 5px;
                color: #555;
                font-weight: bold;
            }
            input[type="url"] {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                box-sizing: border-box;
                font-size: 16px;
            }
            button {
                background-color: #ff0000;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
                width: 100%;
            }
            button:hover:not(:disabled) {
                background-color: #cc0000;
            }
            button:disabled {
                background-color: #999;
                cursor: not-allowed;
            }
            .info {
                margin-top: 20px;
                padding: 15px;
                background-color: #e8f4f8;
                border-radius: 5px;
                display: none;
            }
            .error {
                background-color: #ffe8e8;
                color: #d32f2f;
                padding: 15px;
                border-radius: 5px;
                margin-top: 20px;
                display: none;
            }
            .success {
                background-color: #e8f5e9;
                color: #2e7d32;
                padding: 15px;
                border-radius: 5px;
                margin-top: 20px;
                display: none;
            }
            select {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 16px;
                margin-top: 10px;
            }
            .progress-container {
                margin-top: 20px;
                display: none;
            }
            .progress-bar-wrapper {
                width: 100%;
                height: 30px;
                background-color: #e0e0e0;
                border-radius: 15px;
                overflow: hidden;
                position: relative;
            }
            .progress-bar {
                height: 100%;
                background: linear-gradient(90deg, #ff0000, #ff4444);
                width: 0%;
                transition: width 0.3s ease;
                border-radius: 15px;
            }
            .progress-text {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: #333;
                font-weight: bold;
                font-size: 14px;
            }
            .progress-status {
                text-align: center;
                margin-top: 10px;
                color: #666;
                font-size: 14px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📥 YouTube Video Downloader</h1>
            <form id="downloadForm">
                <div class="form-group">
                    <label for="url">YouTube Video URL:</label>
                    <input type="url" id="url" name="url" placeholder="https://www.youtube.com/watch?v=..." required>
                </div>
                <div class="form-group">
                    <label for="quality">Quality:</label>
                    <select id="quality" name="quality">
                        <option value="highest">Highest Available</option>
                        <option value="720p">720p</option>
                        <option value="480p">480p</option>
                        <option value="360p">360p</option>
                        <option value="240p">240p</option>
                        <option value="144p">144p</option>
                        <option value="lowest">Lowest Available</option>
                    </select>
                </div>
                <button type="submit" id="downloadBtn">Download Video</button>
            </form>
            <div id="info" class="info"></div>
            <div id="error" class="error"></div>
            <div id="success" class="success"></div>
            <div id="progressContainer" class="progress-container">
                <div class="progress-bar-wrapper">
                    <div id="progressBar" class="progress-bar"></div>
                    <div id="progressText" class="progress-text">0%</div>
                </div>
                <div id="progressStatus" class="progress-status">Initializing...</div>
            </div>
        </div>
        <script>
            let currentDownloadId = null;
            let progressInterval = null;

            function formatTime(seconds) {
                const mins = Math.floor(seconds / 60);
                const secs = seconds % 60;
                return mins + ':' + secs.toString().padStart(2, '0');
            }

            function updateProgressBar(progress, status) {
                const progressBar = document.getElementById('progressBar');
                const progressText = document.getElementById('progressText');
                const progressStatus = document.getElementById('progressStatus');
                const progressContainer = document.getElementById('progressContainer');

                progressContainer.style.display = 'block';
                progressBar.style.width = progress + '%';
                progressText.textContent = Math.round(progress) + '%';
                
                const statusMessages = {
                    'initializing': 'Initializing download...',
                    'fetching_streams': 'Fetching video streams...',
                    'downloading': 'Downloading video...',
                    'completed': 'Download complete!',
                    'error': 'Error occurred'
                };
                progressStatus.textContent = statusMessages[status] || status;
            }

            function checkProgress(downloadId) {
                fetch(`/api/progress/${downloadId}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            updateProgressBar(data.progress, data.status);
                            
                            if (data.status === 'completed') {
                                clearInterval(progressInterval);
                                document.getElementById('downloadBtn').disabled = false;
                                document.getElementById('success').textContent = 'Video downloaded successfully! Starting download...';
                                document.getElementById('success').style.display = 'block';
                                // Automatically download the file
                                window.location.href = `/api/download/${downloadId}/file`;
                            } else if (data.status === 'error') {
                                clearInterval(progressInterval);
                                document.getElementById('downloadBtn').disabled = false;
                                document.getElementById('error').textContent = 'Error: Download failed';
                                document.getElementById('error').style.display = 'block';
                                document.getElementById('progressContainer').style.display = 'none';
                            }
                        }
                    })
                    .catch(error => {
                        console.error('Progress check error:', error);
                    });
            }

            document.getElementById('downloadForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const url = document.getElementById('url').value;
                const quality = document.getElementById('quality').value;
                const errorDiv = document.getElementById('error');
                const infoDiv = document.getElementById('info');
                const successDiv = document.getElementById('success');
                const downloadBtn = document.getElementById('downloadBtn');
                
                errorDiv.style.display = 'none';
                infoDiv.style.display = 'none';
                successDiv.style.display = 'none';
                downloadBtn.disabled = true;
                
                // Clear any existing progress interval
                if (progressInterval) {
                    clearInterval(progressInterval);
                }
                
                try {
                    // First get video info
                    const infoResponse = await fetch(`/api/info?url=${encodeURIComponent(url)}`);
                    const infoData = await infoResponse.json();
                    
                    if (!infoData.success) {
                        errorDiv.textContent = 'Error: ' + infoData.error;
                        errorDiv.style.display = 'block';
                        downloadBtn.disabled = false;
                        return;
                    }
                    
                    // Show info
                    infoDiv.innerHTML = `<strong>Title:</strong> ${infoData.video.title}<br>
                                        <strong>Author:</strong> ${infoData.video.author}<br>
                                        <strong>Duration:</strong> ${formatTime(infoData.video.length)}<br>
                                        <strong>Views:</strong> ${infoData.video.views.toLocaleString()}`;
                    infoDiv.style.display = 'block';
                    
                    // Start download
                    const downloadResponse = await fetch('/api/download', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ url: url, quality: quality })
                    });
                    
                    const downloadData = await downloadResponse.json();
                    
                    if (!downloadData.success) {
                        errorDiv.textContent = 'Error: ' + downloadData.error;
                        errorDiv.style.display = 'block';
                        downloadBtn.disabled = false;
                        return;
                    }
                    
                    currentDownloadId = downloadData.download_id;
                    updateProgressBar(0, 'initializing');
                    
                    // Start polling for progress
                    progressInterval = setInterval(() => {
                        checkProgress(currentDownloadId);
                    }, 500);
                    
                    // Also check immediately
                    checkProgress(currentDownloadId);
                    
                } catch (error) {
                    errorDiv.textContent = 'Error: ' + error.message;
                    errorDiv.style.display = 'block';
                    downloadBtn.disabled = false;
                }
            });
        </script>
    </body>
    </html>
    '''


@app.route('/api/info', methods=['GET'])
def api_info():
    """API endpoint to get video information"""
    url = request.args.get('url')
    
    if not url:
        return jsonify({'success': False, 'error': 'URL parameter is required'}), 400
    
    video_info, error = get_video_info(url)
    
    if error:
        return jsonify({'success': False, 'error': error}), 400
    
    return jsonify({'success': True, 'video': video_info})


@app.route('/api/download', methods=['POST'])
def api_download():
    """API endpoint to start video download"""
    data = request.get_json()
    url = data.get('url') if data else None
    quality = data.get('quality', 'highest') if data else 'highest'
    itag = data.get('itag') if data else None
    
    if not url:
        return jsonify({'success': False, 'error': 'URL parameter is required'}), 400
    
    # Generate download ID
    download_id = str(uuid.uuid4())
    update_progress(download_id, 0, 'initializing')
    
    # Start download in background thread
    def download_thread():
        download_video(url, download_id, itag=int(itag) if itag else None, quality=quality)
    
    thread = threading.Thread(target=download_thread)
    thread.daemon = True
    thread.start()
    
    return jsonify({'success': True, 'download_id': download_id})


@app.route('/api/download/<download_id>/file', methods=['GET'])
def api_download_file(download_id):
    """API endpoint to get the downloaded file"""
    with progress_lock:
        progress_data = download_progress.get(download_id)
        filepath = download_files.get(download_id)
        
        if not progress_data or progress_data['status'] != 'completed':
            return jsonify({'success': False, 'error': 'Download not completed'}), 404
        
        if not filepath or not os.path.exists(filepath):
            return jsonify({'success': False, 'error': 'File not found'}), 404
    
    try:
        return send_file(
            filepath,
            as_attachment=True,
            download_name=os.path.basename(filepath),
            mimetype='video/mp4'
        )
    finally:
        # Clean up file after sending (with delay to ensure download started)
        def cleanup_file():
            time.sleep(10)  # Wait 10 seconds before cleanup
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except:
                    pass
            with progress_lock:
                download_progress.pop(download_id, None)
                download_files.pop(download_id, None)
        
        cleanup_thread = threading.Thread(target=cleanup_file)
        cleanup_thread.daemon = True
        cleanup_thread.start()


@app.route('/api/progress/<download_id>', methods=['GET'])
def api_progress(download_id):
    """API endpoint to get download progress"""
    with progress_lock:
        progress_data = download_progress.get(download_id)
        if not progress_data:
            return jsonify({'success': False, 'error': 'Download ID not found'}), 404
        
        return jsonify({
            'success': True,
            'progress': progress_data['progress'],
            'status': progress_data['status']
        })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for Render"""
    return jsonify({'status': 'healthy'}), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
