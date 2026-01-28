// Popup script for Tab Group Cloner

document.addEventListener('DOMContentLoaded', async () => {
  // Get DOM elements
  const cloneBtn = document.getElementById('clone-btn');
  const groupCount = document.getElementById('group-count');
  const tabCount = document.getElementById('tab-count');
  const loading = document.getElementById('loading');
  const success = document.getElementById('success');
  const error = document.getElementById('error');
  const successMessage = document.getElementById('success-message');
  const errorMessage = document.getElementById('error-message');
  const helpLink = document.getElementById('help-link');

  // Load current tab stats
  await loadTabStats();

  // Clone button click handler
  cloneBtn.addEventListener('click', async () => {
    try {
      // Show loading state
      cloneBtn.disabled = true;
      hideAllMessages();
      loading.classList.remove('hidden');

      // Send message to background script
      const response = await chrome.runtime.sendMessage({
        action: 'cloneToSidekick'
      });

      // Hide loading
      loading.classList.add('hidden');

      if (response.success) {
        // Show success message
        const data = response.data;
        successMessage.textContent = data.message ||
          `Successfully cloned ${data.groupsCloned || 0} tab groups with ${data.tabsCloned || 0} tabs to Sidekick!`;
        success.classList.remove('hidden');

        // Close popup after 2 seconds
        setTimeout(() => window.close(), 2000);
      } else {
        throw new Error(response.error || 'Unknown error occurred');
      }
    } catch (err) {
      // Hide loading
      loading.classList.add('hidden');

      // Show error message
      errorMessage.textContent = err.message;
      error.classList.remove('hidden');
    } finally {
      cloneBtn.disabled = false;
    }
  });

  // Help link handler
  helpLink.addEventListener('click', (e) => {
    e.preventDefault();
    chrome.tabs.create({
      url: 'https://github.com/yourusername/tab-group-cloner#installation'
    });
  });
});

async function loadTabStats() {
  try {
    const groupCount = document.getElementById('group-count');
    const tabCount = document.getElementById('tab-count');

    // Get current window
    const currentWindow = await chrome.windows.getCurrent();

    // Get all tabs
    const tabs = await chrome.tabs.query({ windowId: currentWindow.id });

    // Get all groups
    const groups = await chrome.tabGroups.query({ windowId: currentWindow.id });

    // Update UI
    groupCount.textContent = groups.length;
    tabCount.textContent = tabs.length;

    // Disable button if no tabs
    if (tabs.length === 0) {
      document.getElementById('clone-btn').disabled = true;
    }
  } catch (err) {
    console.error('Error loading tab stats:', err);
    document.getElementById('group-count').textContent = '?';
    document.getElementById('tab-count').textContent = '?';
  }
}

function hideAllMessages() {
  document.getElementById('loading').classList.add('hidden');
  document.getElementById('success').classList.add('hidden');
  document.getElementById('error').classList.add('hidden');
}
