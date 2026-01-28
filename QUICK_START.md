# Quick Start Guide

Get Tab Group Cloner running in 5 minutes!

## TL;DR

```bash
# 1. Install prerequisites
brew install chromedriver  # macOS
# or download from https://chromedriver.chromium.org/

# 2. Install native host
cd native-host
./install.sh  # macOS/Linux
# or: install.ps1 for Windows

# 3. Load extension in Chrome
# Go to chrome://extensions → Enable Developer Mode → Load Unpacked → Select chrome-extension folder

# 4. Copy your extension ID and update the manifest
# Edit: ~/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.tabcloner.host.json
# Replace EXTENSION_ID_PLACEHOLDER with your actual extension ID

# 5. Done! Click the extension icon to clone tabs
```

## Visual Guide

### 1. Prerequisites

**Install Sidekick:**
- Visit https://www.meetsidekick.com/
- Download and install

**Install ChromeDriver:**
```bash
# macOS
brew install chromedriver

# Windows (via Chocolatey)
choco install chromedriver

# Or download manually from:
# https://chromedriver.chromium.org/
```

### 2. Install Chrome Extension

1. Open Chrome
2. Go to `chrome://extensions`
3. Toggle "Developer mode" ON (top right)
4. Click "Load unpacked"
5. Navigate to this project's `chrome-extension` folder
6. Click "Select"

**Save your Extension ID!** It looks like: `abcdefghijklmnopqrstuvwxyz123456`

### 3. Install Native Host

**macOS/Linux:**
```bash
cd native-host
chmod +x install.sh
./install.sh
```

**Windows:**
```powershell
cd native-host
powershell -ExecutionPolicy Bypass -File install.ps1
```

### 4. Configure Extension ID

Edit the native messaging manifest:

**macOS:**
```bash
nano ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/com.tabcloner.host.json
```

**Linux:**
```bash
nano ~/.config/google-chrome/NativeMessagingHosts/com.tabcloner.host.json
```

**Windows:**
```powershell
notepad %APPDATA%\Google\Chrome\NativeMessagingHosts\com.tabcloner.host.json
```

Replace `EXTENSION_ID_PLACEHOLDER` with your actual extension ID, then save.

### 5. Test It!

1. Create some tab groups in Chrome:
   - Right-click a tab → "Add to new group"
   - Name the group and pick a color

2. Click the Tab Group Cloner extension icon

3. Click "Clone to Sidekick"

4. Watch your tabs open in Sidekick with the same groups!

## Troubleshooting

### Error: "Native host not installed"

**Solution:**
- Restart Chrome completely (close all windows)
- Verify the extension ID in the manifest matches chrome://extensions
- Check the manifest file exists in the correct location

### Error: "Sidekick browser not found"

**Solution:**
- Install Sidekick from https://www.meetsidekick.com/
- If installed in custom location, edit `tab_cloner_host.py` line 22-26 with your path

### Error: "ChromeDriver not found"

**Solution:**
```bash
# macOS
brew install chromedriver

# Verify it's in PATH
which chromedriver

# If not in PATH, add to ~/.zshrc or ~/.bash_profile:
export PATH="$PATH:/usr/local/bin"
```

### Still not working?

Check the logs:
```bash
# macOS/Linux
tail -f ~/tab_cloner_host.log

# Windows
Get-Content $env:USERPROFILE\tab_cloner_host.log -Tail 20 -Wait
```

## Next Steps

- Read [README.md](README.md) for full documentation
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
- Report issues or request features on GitHub

## Tips

- Pin the extension for easy access (click the puzzle icon → pin Tab Group Cloner)
- Create a keyboard shortcut in chrome://extensions → Keyboard shortcuts
- Group related tabs before cloning for better organization
- The extension only clones the current window, not all Chrome windows

Enjoy your newly cloned tabs! 🚀
