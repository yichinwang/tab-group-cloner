// Background service worker for Tab Group Receiver (Sidekick Extension)
// Uses chrome.tabs.group() API to create real tab groups

const SERVER_URL = 'http://127.0.0.1:8768';

// Listen for messages from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'createTabGroups') {
    createTabGroups(message.data)
      .then(result => sendResponse({ success: true, data: result }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }
  if (message.action === 'fetchAndCreate') {
    fetchAndCreateTabs()
      .then(result => sendResponse({ success: true, data: result }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }
});

async function fetchAndCreateTabs() {
  // Fetch pending tab data from server
  const response = await fetch(`${SERVER_URL}/pending`);
  if (!response.ok) {
    throw new Error('No pending tabs to import');
  }
  const data = await response.json();
  if (!data || !data.data) {
    throw new Error('No tab data available');
  }
  return await createTabGroups(data.data);
}

async function createTabGroups(tabData) {
  const groups = tabData.groups || [];
  const ungroupedTabs = tabData.ungroupedTabs || [];

  let tabsCreated = 0;
  let groupsCreated = 0;

  // Create ungrouped tabs first
  for (const tabInfo of ungroupedTabs) {
    const url = tabInfo.url;
    if (url && !url.startsWith('chrome://') && !url.startsWith('chrome-extension://')) {
      try {
        await chrome.tabs.create({ url: url, active: false });
        tabsCreated++;
      } catch (e) {
        console.error('Error creating tab:', e);
      }
    }
  }

  // Create each group with its tabs
  for (const group of groups) {
    const groupTitle = group.title || 'Untitled';
    const groupColor = group.color || 'grey';
    const groupTabs = group.tabs || [];

    if (groupTabs.length === 0) continue;

    const tabIds = [];

    // Create all tabs for this group
    for (const tabInfo of groupTabs) {
      const url = tabInfo.url;
      if (url && !url.startsWith('chrome://') && !url.startsWith('chrome-extension://')) {
        try {
          const tab = await chrome.tabs.create({ url: url, active: false });
          tabIds.push(tab.id);
          tabsCreated++;
        } catch (e) {
          console.error('Error creating tab:', e);
        }
      }
    }

    // Group the tabs
    if (tabIds.length > 0) {
      try {
        const groupId = await chrome.tabs.group({ tabIds: tabIds });

        // Set group properties (title and color)
        await chrome.tabGroups.update(groupId, {
          title: groupTitle,
          color: groupColor
        });

        groupsCreated++;
        console.log(`Created group "${groupTitle}" with ${tabIds.length} tabs`);
      } catch (e) {
        console.error('Error creating group:', e);
      }
    }
  }

  return {
    status: 'success',
    message: `Created ${tabsCreated} tabs in ${groupsCreated} groups`,
    tabsCreated: tabsCreated,
    groupsCreated: groupsCreated
  };
}
