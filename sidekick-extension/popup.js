// Popup script for Tab Group Receiver (Sidekick Extension)

document.addEventListener('DOMContentLoaded', () => {
  const fetchBtn = document.getElementById('fetch-btn');
  const importBtn = document.getElementById('import-btn');
  const jsonInput = document.getElementById('json-input');
  const status = document.getElementById('status');

  // Fetch and import from server
  fetchBtn.addEventListener('click', async () => {
    setStatus('loading', 'Fetching tabs from Chrome...');
    fetchBtn.disabled = true;

    try {
      const response = await chrome.runtime.sendMessage({ action: 'fetchAndCreate' });

      if (response.success) {
        setStatus('success', response.data.message);
      } else {
        setStatus('error', response.error);
      }
    } catch (e) {
      setStatus('error', e.message);
    } finally {
      fetchBtn.disabled = false;
    }
  });

  // Import from pasted JSON
  importBtn.addEventListener('click', async () => {
    const jsonText = jsonInput.value.trim();
    if (!jsonText) {
      setStatus('error', 'Please paste JSON data first');
      return;
    }

    let tabData;
    try {
      tabData = JSON.parse(jsonText);
    } catch (e) {
      setStatus('error', 'Invalid JSON format');
      return;
    }

    setStatus('loading', 'Creating tabs and groups...');
    importBtn.disabled = true;

    try {
      const response = await chrome.runtime.sendMessage({
        action: 'createTabGroups',
        data: tabData
      });

      if (response.success) {
        setStatus('success', response.data.message);
        jsonInput.value = '';
      } else {
        setStatus('error', response.error);
      }
    } catch (e) {
      setStatus('error', e.message);
    } finally {
      importBtn.disabled = false;
    }
  });

  function setStatus(type, message) {
    status.className = 'status ' + type;
    status.textContent = message;
  }
});
