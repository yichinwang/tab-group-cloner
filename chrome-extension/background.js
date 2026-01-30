// Background service worker for Tab Group Cloner extension
// Uses local HTTP server instead of native messaging

const SERVER_URL = 'http://127.0.0.1:8768';

// Listen for messages from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'cloneToSidekick') {
    cloneTabGroupsToSidekick()
      .then(result => sendResponse({ success: true, data: result }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Keep the message channel open for async response
  }
});

async function cloneTabGroupsToSidekick() {
  try {
    // Get current window
    const currentWindow = await chrome.windows.getCurrent();

    // Get all tabs in current window
    const tabs = await chrome.tabs.query({ windowId: currentWindow.id });

    // Get all tab groups in current window
    const groups = await chrome.tabGroups.query({ windowId: currentWindow.id });

    // Organize data
    const tabGroupData = organizeTabGroupData(tabs, groups);

    // Send to local server
    const result = await sendToServer(tabGroupData);

    return result;
  } catch (error) {
    console.error('Error cloning tab groups:', error);
    throw error;
  }
}

function organizeTabGroupData(tabs, groups) {
  const groupMap = new Map();

  // Create map of groups
  groups.forEach(group => {
    groupMap.set(group.id, {
      id: group.id,
      title: group.title,
      color: group.color,
      collapsed: group.collapsed,
      tabs: []
    });
  });

  // Organize tabs into groups or ungrouped
  const ungroupedTabs = [];

  tabs.forEach(tab => {
    const tabData = {
      url: tab.url,
      title: tab.title,
      pinned: tab.pinned,
      index: tab.index
    };

    if (tab.groupId !== chrome.tabGroups.TAB_GROUP_ID_NONE) {
      const group = groupMap.get(tab.groupId);
      if (group) {
        group.tabs.push(tabData);
      }
    } else {
      ungroupedTabs.push(tabData);
    }
  });

  return {
    groups: Array.from(groupMap.values()).filter(g => g.tabs.length > 0),
    ungroupedTabs: ungroupedTabs,
    totalTabs: tabs.length,
    totalGroups: groups.length
  };
}

async function sendToServer(data) {
  console.log('Sending to local server:', SERVER_URL);

  try {
    const response = await fetch(SERVER_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        action: 'cloneToSidekick',
        data: data
      })
    });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }

    const result = await response.json();
    console.log('Server response:', result);

    if (result.status === 'success') {
      return result;
    } else {
      throw new Error(result.error || 'Unknown error from server');
    }
  } catch (error) {
    if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
      throw new Error('Server not running. Please start the server first:\npython3 local-server/server.py');
    }
    throw error;
  }
}
