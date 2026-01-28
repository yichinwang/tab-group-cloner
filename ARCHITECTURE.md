# Tab Group Cloner - Architecture Design

## Overview

A system to clone all tab groups from the current Chrome browser window to a new Sidekick browser window with one click.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Chrome Browser                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │          Tab Group Cloner Extension                    │  │
│  │                                                         │  │
│  │  ┌──────────────┐        ┌──────────────┐            │  │
│  │  │   Popup UI   │───────▶│  Background  │            │  │
│  │  │  (popup.html)│        │   Script     │            │  │
│  │  └──────────────┘        └──────┬───────┘            │  │
│  │                                  │                     │  │
│  └──────────────────────────────────┼─────────────────────┘  │
└───────────────────────────────────┼─────────────────────────┘
                                     │
                          Native Messaging API
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────┐
│               Native Messaging Host (Python)                 │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                  tab_cloner_host.py                    │  │
│  │                                                         │  │
│  │  • Receives tab group data from Chrome extension       │  │
│  │  • Launches Sidekick browser                           │  │
│  │  • Controls Sidekick via Chrome DevTools Protocol      │  │
│  │  • Creates tab groups and opens URLs                   │  │
│  └───────────────────────────────────────────────────────┘  │
└───────────────────────────────────┬─────────────────────────┘
                                     │
                          Chrome DevTools Protocol
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Sidekick Browser                           │
│                                                               │
│  • New window created                                        │
│  • Tab groups recreated with same names/colors              │
│  • All URLs opened in correct groups                        │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. User Clicks Extension Icon

User clicks the "Clone to Sidekick" button in the Chrome extension popup.

### 2. Extension Reads Tab Groups

```javascript
// Chrome Tabs API
const tabs = await chrome.tabs.query({currentWindow: true});
const groups = await chrome.tabGroups.query({windowId: currentWindowId});

// Data structure collected:
{
  groups: [
    {
      id: 123,
      title: "Work",
      color: "blue",
      collapsed: false,
      tabs: [
        {url: "https://example.com", title: "Example", pinned: false},
        ...
      ]
    },
    ...
  ],
  ungroupedTabs: [
    {url: "https://google.com", title: "Google", pinned: true},
    ...
  ]
}
```

### 3. Send to Native Host

Extension sends tab group data to Python helper via Native Messaging:

```javascript
const port = chrome.runtime.connectNative('com.tabcloner.host');
port.postMessage({
  action: 'cloneToSidekick',
  data: tabGroupData
});
```

### 4. Native Host Processes Request

Python script receives data and:
1. Launches Sidekick browser (if not running)
2. Opens new window via CDP
3. Creates tab groups with matching names/colors
4. Opens all URLs in correct groups

### 5. Response to Extension

Native host sends success/error response:

```json
{
  "status": "success",
  "message": "Cloned 5 tab groups with 23 tabs to Sidekick",
  "windowId": "sidekick_window_123"
}
```

## Components

### Chrome Extension

**manifest.json** (Manifest V3)
- Permissions: `tabs`, `tabGroups`, `nativeMessaging`
- Background service worker
- Popup UI

**popup.html/js**
- Simple one-button UI
- Shows status/progress
- Displays success/error messages

**background.js**
- Reads current window's tab groups
- Establishes native messaging connection
- Handles responses from native host

### Native Messaging Host

**tab_cloner_host.py**
- Reads from stdin (Chrome native messaging protocol)
- Writes to stdout (JSON responses)
- Uses `selenium` or `playwright` to control Sidekick
- Creates tab groups via CDP or browser automation

**Installation:**
- Registers with Chrome via registry/config file
- Lives in user's application directory

### Sidekick Browser Integration

**Methods to control Sidekick:**

1. **Chrome DevTools Protocol (CDP)** - Preferred
   - Launch Sidekick with `--remote-debugging-port=9222`
   - Connect via websocket
   - Create tabs and groups programmatically

2. **Selenium/Playwright** - Fallback
   - More robust but slower
   - Uses WebDriver to control browser
   - May require Sidekick WebDriver

## Tab Group Mapping

Chrome and Sidekick both support Chrome Tab Groups API:

**Chrome Colors:** `grey`, `blue`, `red`, `yellow`, `green`, `pink`, `purple`, `cyan`, `orange`

**Mapping Strategy:**
- Direct 1:1 mapping (same color names)
- Preserve group titles
- Preserve collapsed state
- Maintain tab order within groups

## Edge Cases

1. **Sidekick not installed**
   - Detect if Sidekick exists
   - Show error message with download link

2. **Too many tabs**
   - Warn if >50 tabs
   - Option to proceed anyway

3. **Duplicate URLs**
   - Allow duplicates (same as Chrome behavior)

4. **Pinned tabs**
   - Recreate as pinned in Sidekick
   - Maintain position at start

5. **Special URLs**
   - `chrome://` URLs won't work in Sidekick
   - Skip or replace with about:blank

## Security Considerations

- Native messaging host must be signed/verified
- Only accept messages from known extension ID
- Sanitize all URLs before opening
- User confirmation before cloning large number of tabs

## Future Enhancements

- Bi-directional sync (Sidekick → Chrome)
- Selective group cloning
- Session save/restore
- Keyboard shortcut
- Context menu integration
