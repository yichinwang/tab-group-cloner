#!/usr/bin/env python3
"""
Local HTTP server for Tab Group Cloner.
Receives tab data from Chrome extension and serves it to Sidekick extension.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Store pending tab data for Sidekick extension to fetch
pending_tab_data = None

class TabClonerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests - serve pending tab data to Sidekick extension"""
        global pending_tab_data

        if self.path == '/pending':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            if pending_tab_data:
                response = {'status': 'success', 'data': pending_tab_data}
                # Clear pending data after serving
                pending_tab_data = None
                logger.info("Served pending tab data to Sidekick extension")
            else:
                response = {'status': 'empty', 'message': 'No pending tab data'}

            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'status': 'running',
                'hasPendingData': pending_tab_data is not None
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_error(404, 'Not found')

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        """Handle clone request from Chrome extension"""
        global pending_tab_data

        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))

            logger.info(f"Received request: {data.get('action')}")

            if data.get('action') == 'cloneToSidekick':
                tab_data = data.get('data', {})
                groups = tab_data.get('groups', [])
                ungrouped = tab_data.get('ungroupedTabs', [])

                # Store the data for Sidekick extension to fetch
                pending_tab_data = tab_data

                total_tabs = sum(len(g.get('tabs', [])) for g in groups) + len(ungrouped)
                logger.info(f"Stored {len(groups)} groups with {total_tabs} tabs for Sidekick extension")

                result = {
                    'status': 'success',
                    'message': f'Stored {total_tabs} tabs from {len(groups)} groups. Open Sidekick extension and click "Fetch from Chrome" to import.',
                    'groupsCount': len(groups),
                    'tabsCount': total_tabs
                }

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
            else:
                self.send_error(400, 'Unknown action')

        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'error', 'error': str(e)}).encode())

    def log_message(self, format, *args):
        logger.info(f"{self.address_string()} - {format % args}")


def main():
    port = 8768
    server = HTTPServer(('127.0.0.1', port), TabClonerHandler)
    print(f"Tab Group Cloner server running on http://127.0.0.1:{port}")
    print("Keep this terminal open while using the extension")
    print("Press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")


if __name__ == '__main__':
    main()
