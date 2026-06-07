import http.server
import socketserver
import json
import re
import os

PORT = 3000

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        if self.path.startswith('/api/downloads-path'):
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)
            folder = params.get('folder', [''])[0]
            
            try:
                downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
                if folder:
                    resolved_path = os.path.normpath(os.path.join(downloads_dir, folder))
                else:
                    resolved_path = os.path.normpath(downloads_dir)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"path": resolved_path}, ensure_ascii=False).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
        else:
            super().do_GET()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/save-offsets':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                html_path = 'index.html'
                
                if os.path.exists(html_path):
                    with open(html_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    pattern = r'// EMBEDDED_OFFSETS_START.*?// EMBEDDED_OFFSETS_END'
                    replacement = f'// EMBEDDED_OFFSETS_START\nconst EMBEDDED_OFFSETS = {json.dumps(data, indent=4, ensure_ascii=False)};\n// EMBEDDED_OFFSETS_END'
                    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
                    
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
                    print("Bake offsets into index.html successfully.")
                else:
                    self.send_error(404, "index.html not found")
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
        elif self.path == '/api/bake-github-config':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            try:
                data = json.loads(post_data.decode('utf-8'))
                html_path = 'index.html'
                
                if os.path.exists(html_path):
                    with open(html_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    pattern = r'// GITHUB_SYNC_CONFIG_START.*?// GITHUB_SYNC_CONFIG_END'
                    replacement = f'// GITHUB_SYNC_CONFIG_START\nconst GITHUB_SYNC_CONFIG = {json.dumps(data, indent=4, ensure_ascii=False)};\n// GITHUB_SYNC_CONFIG_END'
                    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
                    
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
                    print("Bake GitHub config into index.html successfully.")
                else:
                    self.send_error(404, "index.html not found")
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(str(e).encode('utf-8'))
        else:
            self.send_error(404)

# Always serve from the directory containing server.py to avoid path issues
os.chdir(os.path.dirname(os.path.abspath(__file__)))

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Custom server serving at port {PORT}")
    httpd.serve_forever()
