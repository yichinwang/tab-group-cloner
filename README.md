# Tab Group Cloner

Clone all tab groups from Chrome browser to Sidekick browser with one click, preserving group names and colors.

## Architecture

```
Chrome Extension  →  Local Server  →  Sidekick Extension
(exports tabs)       (relay)          (creates tab groups)
```

## Components

### 1. Chrome Extension (`chrome-extension/`)
Exports all tabs and tab groups from Chrome to the local server.

### 2. Local Server (`local-server/`)
Python HTTP server that relays tab data between browsers.

### 3. Sidekick Extension (`sidekick-extension/`)
Receives tab data and creates real tab groups using Chrome's `chrome.tabs.group()` API.

## Installation

### Step 1: Install Chrome Extension
1. Open Chrome → `chrome://extensions`
2. Enable "Developer mode"
3. Click "Load unpacked" → Select `chrome-extension/` folder

### Step 2: Install Sidekick Extension
1. Open Sidekick → `sidekick://extensions`
2. Enable "Developer mode"
3. Click "Load unpacked" → Select `sidekick-extension/` folder

### Step 3: Start Local Server
```bash
cd local-server
python3 server.py
```

The server runs on `http://127.0.0.1:8765`

## Usage

1. **Start the local server** (keep terminal open)
2. **In Chrome**: Click the "Tab Group Cloner" extension icon → Click "Clone to Sidekick"
3. **In Sidekick**: Click the "Tab Group Receiver" extension icon → Click "Fetch from Chrome"

Your tabs will be created in Sidekick with matching groups, names, and colors!

## Features

- Clones all tabs from the current Chrome window
- Preserves tab group names and colors
- Supports ungrouped tabs
- Filters out internal browser pages (`chrome://`, `chrome-extension://`)

## Requirements

- Python 3.6+
- Chrome browser
- Sidekick browser

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/pending` | GET | Fetch pending tab data (Sidekick extension) |
| `/status` | GET | Check server status |
| `/` | POST | Store tab data (Chrome extension) |

## License

MIT
