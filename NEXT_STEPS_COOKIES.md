# Next Steps - cookies.txt is Ready!

## ✅ cookies.txt is Ready!

Your cookies file is correct and has been copied to the project folder.

---

## Step 1: Upload cookies.txt to EC2

**On Windows PowerShell:**
```powershell
cd C:\xampp\htdocs\video-download-2

# Upload cookies.txt to EC2
scp -i C:\Users\94765\Desktop\key-instance.pem cookies.txt ubuntu@51.20.116.26:~/flask-app/video-download/
```

---

## Step 2: Upload app.py (if you haven't already)

```powershell
# Upload updated app.py (with cookie support)
scp -i C:\Users\94765\Desktop\key-instance.pem app.py ubuntu@51.20.116.26:~/flask-app/video-download/
```

---

## Step 3: SSH into EC2

```powershell
ssh -i C:\Users\94765\Desktop\key-instance.pem ubuntu@51.20.116.26
```

---

## Step 4: Update Service File

**On EC2:**
```bash
sudo nano /etc/systemd/system/youtube-downloader.service
```

**Find this line:**
```
Environment="PATH=/home/ubuntu/flask-app/video-download/venv/bin"
```

**Change it to this (add the COOKIES_FILE part):**
```
Environment="PATH=/home/ubuntu/flask-app/video-download/venv/bin" "COOKIES_FILE=/home/ubuntu/flask-app/video-download/cookies.txt"
```

**Save:**
- Press `Ctrl+X`
- Press `Y` to confirm
- Press `Enter` to save

---

## Step 5: Restart Service

**On EC2:**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Restart the service
sudo systemctl restart youtube-downloader

# Check status (should show "active (running)")
sudo systemctl status youtube-downloader
```

---

## Step 6: Test!

1. Open your browser
2. Go to: `http://51.20.116.26:5000`
3. Try downloading a YouTube video
4. It should work now! 🎉

---

## Quick Checklist

- [x] ✅ cookies.txt file is correct (DONE!)
- [ ] Upload cookies.txt to EC2
- [ ] Upload app.py to EC2 (if not done)
- [ ] Update service file (add COOKIES_FILE)
- [ ] Restart service
- [ ] Test in browser

---

## If Something Goes Wrong

**Check if cookies file exists on EC2:**
```bash
ls -la ~/flask-app/video-download/cookies.txt
```

**Check service logs:**
```bash
sudo journalctl -u youtube-downloader -n 50 --no-pager
```

**Test cookies manually:**
```bash
cd ~/flask-app/video-download
source venv/bin/activate
yt-dlp --cookies cookies.txt "https://www.youtube.com/watch?v=VIDEO_ID" --list-formats
```
