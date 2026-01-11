# PowerShell Script to Connect to EC2 Instance
# Your EC2 Details:
# - IP: 51.20.116.26
# - Username: ubuntu
# - Key file: key-instance.pem

Write-Host "=== EC2 Connection Helper ===" -ForegroundColor Green
Write-Host ""

# Step 1: Find key file
Write-Host "Step 1: Searching for key-instance.pem..." -ForegroundColor Yellow
$keyFiles = Get-ChildItem -Path $env:USERPROFILE -Filter *.pem -Recurse -ErrorAction SilentlyContinue | Where-Object { $_.Name -like "*key*" -or $_.Name -like "*instance*" }

if ($keyFiles) {
    Write-Host "Found key file(s):" -ForegroundColor Green
    $keyFiles | ForEach-Object { Write-Host "  - $($_.FullName)" -ForegroundColor Cyan }
    $keyFile = $keyFiles[0].FullName
    Write-Host "`nUsing: $keyFile" -ForegroundColor Green
} else {
    Write-Host "Key file not found automatically." -ForegroundColor Red
    Write-Host "Please enter the full path to your key-instance.pem file:" -ForegroundColor Yellow
    $keyFile = Read-Host "Path"
}

if (-not (Test-Path $keyFile)) {
    Write-Host "Error: Key file not found at: $keyFile" -ForegroundColor Red
    exit
}

# Step 2: Set permissions
Write-Host "`nStep 2: Setting key file permissions..." -ForegroundColor Yellow
try {
    icacls $keyFile /inheritance:r 2>&1 | Out-Null
    icacls $keyFile /grant:r "$env:USERNAME`:R" 2>&1 | Out-Null
    Write-Host "Permissions set successfully!" -ForegroundColor Green
} catch {
    Write-Host "Warning: Could not set permissions. Trying anyway..." -ForegroundColor Yellow
}

# Step 3: Connect
Write-Host "`nStep 3: Connecting to EC2 instance..." -ForegroundColor Yellow
Write-Host "Server: ubuntu@51.20.116.26" -ForegroundColor Cyan
Write-Host "Key file: $keyFile" -ForegroundColor Cyan
Write-Host ""
Write-Host "Connecting in 3 seconds... (Press Ctrl+C to cancel)" -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Connect via SSH
ssh -i $keyFile ubuntu@51.20.116.26
