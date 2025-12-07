import http.server
import socketserver
import json
import sys
import os

# add parent directory to path for mongodb_storage import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mongodb_storage import MongoDBStorage

PORT = 8000

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self): # handle POST requests
        if self.path == '/api/signup':
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length).decode('utf-8')
            try:
                data = json.loads(body)
                first_name = data.get('firstName', '').strip()
                email = data.get('email', '').strip()
                if not first_name or not email:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "First name and email are required"}).encode())
                    return
                # save to mongodb:
                db = MongoDBStorage()
                user_id = db.save_user(first_name, email)
                if user_id:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True, "message": f"Thanks {first_name}! Check your email for updates."}).encode())
                else:
                    self.send_response(500)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Failed to save user"}).encode())
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_GET(self): # handle GET requests
        if self.path == '/':
            self.path = '/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

Handler = CustomHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server running at http://localhost:{PORT}")
    httpd.serve_forever()