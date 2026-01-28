#!/usr/bin/env python3
"""
Test script to simulate Chrome calling the native messaging host.
Run this to verify the native host works correctly.
"""

import subprocess
import struct
import json
import sys

def send_message(process, message):
    """Send a message to the native host."""
    encoded = json.dumps(message).encode('utf-8')
    process.stdin.write(struct.pack('I', len(encoded)))
    process.stdin.write(encoded)
    process.stdin.flush()

def read_message(process):
    """Read a message from the native host."""
    # Read length
    length_bytes = process.stdout.read(4)
    if len(length_bytes) < 4:
        return None
    length = struct.unpack('I', length_bytes)[0]
    # Read message
    message = process.stdout.read(length).decode('utf-8')
    return json.loads(message)

def main():
    # Path to wrapper script
    wrapper_path = '/Users/ycw/Documents/Claude_PRJ/claude-code/tab-group-cloner/native-host/tab_cloner_host_wrapper.sh'

    print("Testing native messaging host...")
    print(f"Wrapper: {wrapper_path}")
    print()

    # Test message (minimal tab group data)
    test_message = {
        "action": "cloneToSidekick",
        "data": {
            "groups": [
                {
                    "id": 1,
                    "title": "Test Group",
                    "color": "blue",
                    "collapsed": False,
                    "tabs": [
                        {"url": "https://www.google.com", "title": "Google", "pinned": False}
                    ]
                }
            ],
            "ungroupedTabs": [],
            "totalTabs": 1,
            "totalGroups": 1
        }
    }

    print("Sending test message:")
    print(json.dumps(test_message, indent=2))
    print()

    try:
        # Start the native host process
        process = subprocess.Popen(
            [wrapper_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Send test message
        send_message(process, test_message)

        # Wait for response (with timeout)
        import select
        if select.select([process.stdout], [], [], 30)[0]:
            response = read_message(process)
            print("Response received:")
            print(json.dumps(response, indent=2))
        else:
            print("Timeout waiting for response")
            stderr = process.stderr.read().decode('utf-8')
            if stderr:
                print(f"Stderr: {stderr}")

        process.terminate()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
