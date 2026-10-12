import http.server
import socketserver
import urllib.request
import urllib.error
import os
import sys

PORT = 8000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class SiteHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # Support clean URL /encomendar
        if self.path == '/encomendar' or self.path == '/encomendar/':
            self.path = '/encomendar/index.html'
        return super().do_GET()

    def do_POST(self):
        # Forward _serverFn to lovable backend or handle fallback
        if self.path.startswith('/_serverFn/'):
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            target_url = f"https://ganharnovosalario.lovable.app{self.path}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
                'Content-Type': self.headers.get('Content-Type', 'application/json'),
                'x-tsr-serverFn': self.headers.get('x-tsr-serverFn', 'true'),
                'Accept': self.headers.get('Accept', 'application/json')
            }
            try:
                req = urllib.request.Request(target_url, data=body, headers=headers, method='POST')
                with urllib.request.urlopen(req) as resp:
                    resp_data = resp.read()
                    self.send_response(resp.status)
                    for k, v in resp.headers.items():
                        if k.lower() not in ['content-length', 'transfer-encoding', 'connection']:
                            self.send_header(k, v)
                    self.send_header('Content-Length', str(len(resp_data)))
                    self.end_headers()
                    self.wfile.write(resp_data)
                    return
            except Exception as e:
                # If remote is unreachable, return a mock success Seroval response with UUID
                import uuid
                ref_id = f"local_{uuid.uuid4().hex[:12]}"
                # Return JSON response format
                mock_resp = f'{{"id":"{ref_id}"}}'.encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('x-tss-raw', 'true')
                self.send_header('Content-Length', str(len(mock_resp)))
                self.end_headers()
                self.wfile.write(mock_resp)
                return
        
        return super().do_POST()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), SiteHandler) as httpd:
        print(f"==================================================")
        print(f"  Site clonado rodando com sucesso!")
        print(f"  URL Local: http://localhost:{port}")
        print(f"  Página Encomendar: http://localhost:{port}/encomendar")
        print(f"  Pressione Ctrl+C para encerrar")
        print(f"==================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor encerrado.")
