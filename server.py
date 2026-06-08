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

# Serve from directory of the script or compiled exe
import sys
import urllib.request

import shutil

if getattr(sys, 'frozen', False):
    exe_dir = os.path.dirname(sys.executable)
else:
    exe_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(exe_dir)

# 1. Try to auto-update index.html from GitHub using config if available
owner, repo, branch, token = '', '', 'main', ''
if os.path.exists('git_config.json'):
    try:
        with open('git_config.json', 'r', encoding='utf-8') as f:
            cfg = json.load(f)
            owner = cfg.get('owner', '')
            repo = cfg.get('repo', '')
            branch = cfg.get('branch', 'main')
            token = cfg.get('token', '')
        print("Loaded GitHub config from git_config.json.")
    except Exception as e:
        print(f"Error reading git_config.json: {e}")

if not owner or not repo:
    owner = "dudo011"
    repo = "map-capture"
    branch = "main"

if not token:
    token = "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"

print("Checking for index.html updates from GitHub...")
update_success = False
try:
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/index.html"
    req = urllib.request.Request(url)
    if token:
        req.add_header("Authorization", f"token {token}")
    req.add_header("User-Agent", "Mozilla/5.0")
    
    with urllib.request.urlopen(req, timeout=5) as response:
        html_content = response.read()
        with open('index.html', 'wb') as f:
            f.write(html_content)
    print("Successfully updated index.html to the latest version from GitHub.")
    update_success = True
except Exception as e:
    print(f"Could not auto-update index.html from GitHub: {e}")

# 2. Fallback: If GitHub update failed, always overwrite with the bundled copy
if not update_success and getattr(sys, 'frozen', False):
    try:
        bundled_path = os.path.join(sys._MEIPASS, 'index.html')
        if os.path.exists(bundled_path):
            def get_version(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        c = f.read()
                    m = re.search(r'지적도 캡처 자동화 v(\d+\.\d+)', c)
                    return float(m.group(1)) if m else 0.0
                except:
                    return 0.0

            local_ver = get_version('index.html') if os.path.exists('index.html') else 0.0
            bundled_ver = get_version(bundled_path)

            print(f"Local index.html version: v{local_ver}")
            print(f"Bundled index.html version: v{bundled_ver}")

            # Always overwrite local with bundled when GitHub update failed
            shutil.copy(bundled_path, 'index.html')
            print(f"-> Overwrote local index.html with bundled v{bundled_ver} (local was v{local_ver}).")
    except Exception as err:
        print(f"Failed to extract bundled index.html: {err}")

import threading
import webbrowser

def open_browser():
    try:
        print("Opening web browser automatically...")
        webbrowser.open(f"http://localhost:{PORT}/index.html")
    except Exception as e:
        print(f"Failed to open browser automatically: {e}")

# Start a timer to open the browser 1.2 seconds after launching the server
threading.Timer(1.2, open_browser).start()

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Custom server serving at port {PORT}")
    httpd.serve_forever()
