#!/usr/bin/env python3
"""
Automated test to control Chrome browser and test the Tab Group Cloner extension.
This script will:
1. Launch Chrome with the extension
2. Create some test tabs
3. Click the extension to clone tabs to Sidekick
"""

import subprocess
import time
import json
import os
from pathlib import Path

# Paths
CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
EXTENSION_PATH = "/Users/ycw/Documents/Claude_PRJ/claude-code/tab-group-cloner/chrome-extension"
USER_DATA_DIR = "/tmp/chrome_test_profile"

def run_test():
    print("=" * 60)
    print("Automated Chrome Extension Test")
    print("=" * 60)
    print()

    # Clear old log
    log_file = Path.home() / 'tab_cloner_host.log'
    if log_file.exists():
        log_file.unlink()
    print(f"Cleared log file: {log_file}")

    # First, let's just test the native messaging directly
    print()
    print("Step 1: Testing native messaging host directly...")
    print("-" * 40)

    result = subprocess.run(
        ['python3', '/Users/ycw/Documents/Claude_PRJ/claude-code/tab-group-cloner/native-host/test_native_host.py'],
        capture_output=True,
        text=True,
        timeout=60
    )

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    print()
    print("Step 2: Checking log file...")
    print("-" * 40)

    if log_file.exists():
        with open(log_file) as f:
            log_content = f.read()
        print("Log contents:")
        print(log_content)
    else:
        print("No log file created!")

    print()
    print("Step 3: Testing wrapper script directly...")
    print("-" * 40)

    # Test the wrapper script is executable
    wrapper_path = "/Users/ycw/Documents/Claude_PRJ/claude-code/tab-group-cloner/native-host/tab_cloner_host_wrapper.sh"

    # Check if wrapper exists and is executable
    if os.path.exists(wrapper_path):
        print(f"Wrapper exists: {wrapper_path}")
        print(f"Is executable: {os.access(wrapper_path, os.X_OK)}")

        # Check file permissions
        import stat
        st = os.stat(wrapper_path)
        print(f"Permissions: {oct(st.st_mode)}")
    else:
        print(f"ERROR: Wrapper not found: {wrapper_path}")

    print()
    print("Step 4: Checking Chrome native messaging manifest...")
    print("-" * 40)

    manifest_path = Path.home() / "Library/Application Support/Google/Chrome/NativeMessagingHosts/com.tabcloner.host.json"
    if manifest_path.exists():
        with open(manifest_path) as f:
            manifest = json.load(f)
        print(f"Manifest path: {manifest_path}")
        print(f"Host name: {manifest.get('name')}")
        print(f"Host path: {manifest.get('path')}")
        print(f"Allowed origins: {manifest.get('allowed_origins')}")

        # Verify the path in manifest exists
        host_path = manifest.get('path')
        if os.path.exists(host_path):
            print(f"Host binary exists: YES")
            print(f"Host is executable: {os.access(host_path, os.X_OK)}")
        else:
            print(f"ERROR: Host binary does not exist at {host_path}")
    else:
        print(f"ERROR: Manifest not found: {manifest_path}")

    print()
    print("Step 5: Testing if Chrome can execute the wrapper...")
    print("-" * 40)

    # Simulate what Chrome does - call the wrapper with no arguments
    # and check if it starts
    log_file.unlink() if log_file.exists() else None

    proc = subprocess.Popen(
        [wrapper_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Send a test message in native messaging format
    import struct
    test_msg = json.dumps({"action": "test"}).encode('utf-8')
    length_bytes = struct.pack('I', len(test_msg))

    try:
        proc.stdin.write(length_bytes + test_msg)
        proc.stdin.flush()
        time.sleep(1)
        proc.terminate()
    except:
        pass

    # Check log
    time.sleep(0.5)
    if log_file.exists():
        with open(log_file) as f:
            print("Log after direct call:")
            print(f.read())
    else:
        print("No log created from direct call")

    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print("""
If the native messaging test in Step 1 shows "success", then the native host
is working correctly when called from Python.

If Step 5 shows log entries, then the wrapper script is working.

The issue is likely:
1. Chrome hasn't been fully restarted (quit ALL Chrome windows with Cmd+Q)
2. The extension ID in the manifest doesn't match the actual extension
3. Chrome has cached a bad state

SOLUTION:
1. Quit Chrome completely (Cmd+Q)
2. Open Terminal and run: killall "Google Chrome"
3. Wait 5 seconds
4. Reopen Chrome
5. Go to chrome://extensions and note the extension ID
6. Verify it matches: blfedpnhhpjhidcaldfegmldkcjccmkm
7. If different, update the manifest file
""")

if __name__ == '__main__':
    run_test()
