#!/usr/bin/env python3
"""
Native messaging host for Tab Group Cloner Chrome extension.
Receives tab group data from Chrome and clones them to Sidekick browser.
Uses Playwright for browser automation (no manual driver installation needed).
"""

# Early startup logging - write immediately to catch any issues
import os
from pathlib import Path
_early_log = Path.home() / 'tab_cloner_host.log'
with open(_early_log, 'a') as f:
    f.write(f"Script starting at {__file__}\n")

import sys
import json
import struct
import logging
import subprocess
import time
import platform

# Configure logging
logging.basicConfig(
    filename=str(Path.home() / 'tab_cloner_host.log'),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Sidekick browser paths (platform-specific)
SIDEKICK_PATHS = {
    'darwin': '/Applications/Sidekick.app/Contents/MacOS/Sidekick',
    'win32': r'C:\Program Files\Sidekick\Application\sidekick.exe',
    'linux': '/usr/bin/sidekick'
}


def send_message(message):
    """Send a message to Chrome extension via stdout."""
    encoded_message = json.dumps(message).encode('utf-8')
    sys.stdout.buffer.write(struct.pack('I', len(encoded_message)))
    sys.stdout.buffer.write(encoded_message)
    sys.stdout.buffer.flush()
    logging.info(f"Sent message: {message}")

def _read_exact(stream, size):
    """Read exactly size bytes from stream or return None on EOF."""
    chunks = []
    remaining = size
    while remaining > 0:
        chunk = stream.read(remaining)
        if not chunk:
            return None
        chunks.append(chunk)
        remaining -= len(chunk)
    return b''.join(chunks)

def read_message():
    """Read a message from Chrome extension via stdin."""
    # Read the message length (first 4 bytes)
    text_length_bytes = _read_exact(sys.stdin.buffer, 4)
    if not text_length_bytes:
        return None

    text_length = struct.unpack('I', text_length_bytes)[0]
    text_bytes = _read_exact(sys.stdin.buffer, text_length)
    if text_bytes is None:
        return None
    text = text_bytes.decode('utf-8')
    message = json.loads(text)
    logging.info(f"Received message: {message}")
    return message


def find_sidekick_binary():
    """Find the Sidekick browser binary."""
    system = platform.system().lower()

    if system == 'darwin':
        path = SIDEKICK_PATHS['darwin']
    elif system == 'windows':
        path = SIDEKICK_PATHS['win32']
    else:
        path = SIDEKICK_PATHS['linux']

    if Path(path).exists():
        return path

    # Try to find via which command (macOS/Linux)
    try:
        result = subprocess.run(['which', 'sidekick'], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass

    return None


def clone_tabs_to_sidekick(tab_group_data):
    """Clone tab groups to Sidekick browser using Playwright."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {
            'status': 'error',
            'error': 'Playwright not installed. Run: pip install playwright && playwright install chromium'
        }

    try:
        # Find Sidekick binary
        sidekick_path = find_sidekick_binary()
        if not sidekick_path:
            return {
                'status': 'error',
                'error': 'Sidekick browser not found. Please install Sidekick from https://www.meetsidekick.com/'
            }

        logging.info(f"Found Sidekick at: {sidekick_path}")

        groups = tab_group_data.get('groups', [])
        ungrouped_tabs = tab_group_data.get('ungroupedTabs', [])

        tabs_cloned = 0
        groups_cloned = 0

        with sync_playwright() as p:
            # Launch Sidekick browser using Playwright
            # Sidekick is Chromium-based, so we use the chromium channel with custom executable
            try:
                browser = p.chromium.launch(
                    executable_path=sidekick_path,
                    headless=False,  # We want to see the browser
                    args=['--disable-blink-features=AutomationControlled']
                )
                logging.info("Launched Sidekick browser successfully")
            except Exception as e:
                logging.error(f"Failed to launch Sidekick: {e}")
                return {
                    'status': 'error',
                    'error': f'Failed to launch Sidekick browser: {str(e)}'
                }

            # Create a new browser context and page
            context = browser.new_context()

            # Collect all URLs to open
            all_urls = []

            # Add ungrouped tabs
            for tab_data in ungrouped_tabs:
                url = tab_data.get('url', '')
                # Skip special Chrome URLs
                if url.startswith('chrome://') or url.startswith('chrome-extension://'):
                    logging.warning(f"Skipping special URL: {url}")
                    continue
                if url:
                    all_urls.append(('ungrouped', url, tab_data.get('title', '')))

            # Add grouped tabs
            for group in groups:
                group_title = group.get('title', 'Untitled')
                group_tabs = group.get('tabs', [])

                for tab_data in group_tabs:
                    url = tab_data.get('url', '')
                    # Skip special Chrome URLs
                    if url.startswith('chrome://') or url.startswith('chrome-extension://'):
                        logging.warning(f"Skipping special URL: {url}")
                        continue
                    if url:
                        all_urls.append((group_title, url, tab_data.get('title', '')))

            logging.info(f"Opening {len(all_urls)} URLs in Sidekick")

            # Open first URL in the initial page
            if all_urls:
                first_page = context.new_page()
                group_name, url, title = all_urls[0]
                try:
                    first_page.goto(url, wait_until='domcontentloaded', timeout=30000)
                    tabs_cloned += 1
                    logging.info(f"Opened: {url}")
                except Exception as e:
                    logging.error(f"Error opening {url}: {e}")

            # Open remaining URLs in new tabs
            for group_name, url, title in all_urls[1:]:
                try:
                    page = context.new_page()
                    page.goto(url, wait_until='domcontentloaded', timeout=30000)
                    tabs_cloned += 1
                    logging.info(f"Opened: {url}")
                    time.sleep(0.2)  # Small delay between tabs
                except Exception as e:
                    logging.error(f"Error opening {url}: {e}")

            groups_cloned = len(groups)

            logging.info(f"Successfully cloned {groups_cloned} groups with {tabs_cloned} tabs")

            # Keep browser open (don't close it)
            # The user can manage the browser from here
            # We detach by not calling browser.close()

        return {
            'status': 'success',
            'message': f'Opened {tabs_cloned} tabs from {groups_cloned} groups in Sidekick',
            'groupsCloned': groups_cloned,
            'tabsCloned': tabs_cloned
        }

    except Exception as e:
        logging.error(f"Error cloning tabs: {e}", exc_info=True)
        return {
            'status': 'error',
            'error': str(e)
        }


def main():
    """Main entry point for the native messaging host."""
    logging.info("Native messaging host started")

    try:
        while True:
            message = read_message()
            if message is None:
                logging.info("No more messages, exiting")
                break

            action = message.get('action')
            data = message.get('data')

            if action == 'cloneToSidekick':
                logging.info("Processing cloneToSidekick request")
                result = clone_tabs_to_sidekick(data)
                send_message(result)
            else:
                send_message({
                    'status': 'error',
                    'error': f'Unknown action: {action}'
                })

    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
        send_message({
            'status': 'error',
            'error': str(e)
        })
        sys.exit(1)


if __name__ == '__main__':
    main()
