# Deploy to AWS EC2 - Step by Step Guide

## Option 1: Using Git/GitHub (Recommended)

### Step 1: Install Git (if not installed)
- Download from: https://git-scm.com/download/win
- Install with default options

### Step 2: Initialize Git and Push to GitHub

**On your local machine (Windows):**

```powershell
# Navigate to project directory
cd C:\xampp\htdocs\video-download-2

# Initialize git repository
git init

# Add all files
git add .

# Commit files
git commit -m "Initial commit - YouTube downloader with yt-dlp"

# Create a repository on GitHub.com (go to github.com, click New Repository)
# Then add remote and push:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

**Note:** Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` with your actual GitHub username and repository name.

### Step 3: Pull on AWS EC2

**SSH into your EC2 instance:**
```bash
ssh -i C:\Users\94765\Desktop\key-instance.pem ubuntu@51.20.116.26
```

**On EC2, navigate to your project directory:**
```bash
cd ~/flask-app/video-download

# Pull the latest code
git pull origin main

# Or if you haven't cloned yet:
# git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git ~/flask-app/video-download
```

**Update dependencies:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Restart the service:**
```bash
sudo systemctl restart youtube-downloader
sudo systemctl status youtube-downloader
```

---

## Option 2: Manual Upload (Using SCP)

**On Windows PowerShell:**

```powershell
cd C:\xampp\htdocs\video-download-2

# Upload files to EC2
scp -i C:\Users\94765\Desktop\key-instance.pem app.py requirements.txt ubuntu@51.20.116.26:~/flask-app/video-download/

# Or upload all files at once:
scp -i C:\Users\94765\Desktop\key-instance.pem *.py *.txt *.yaml *.service ubuntu@51.20.116.26:~/flask-app/video-download/
```

**Then on EC2:**
```bash
ssh -i C:\Users\94765\Desktop\key-instance.pem ubuntu@51.20.116.26
cd ~/flask-app/video-download
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart youtube-downloader
sudo systemctl status youtube-downloader
```

---

## Files to Upload

Essential files:
- ✅ `app.py` - Main application (updated with yt-dlp, no ffmpeg needed)
- ✅ `requirements.txt` - Dependencies (includes yt-dlp)
- ✅ `youtube-downloader.service` - systemd service file
- ✅ `README.md` - Documentation (optional)
- ✅ `render.yaml` - For Render.com deployment (optional)

---

## Quick Summary

**After uploading to EC2:**
1. ✅ Files are uploaded
2. ✅ Install dependencies: `pip install -r requirements.txt`
3. ✅ Restart service: `sudo systemctl restart youtube-downloader`
4. ✅ Check status: `sudo systemctl status youtube-downloader`
5. ✅ Test: Visit `http://51.20.116.26:5000` in your browser

**Note:** The updated code now uses yt-dlp without requiring ffmpeg, so downloads should work on EC2!
