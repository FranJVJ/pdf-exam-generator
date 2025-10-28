from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("DEBUG: TEST endpoint called with GET")
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {"message": "Test endpoint working", "method": "GET"}
        self.wfile.write(json.dumps(response).encode())
    
    def do_POST(self):
        print("DEBUG: TEST endpoint called with POST")
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {"message": "Test endpoint working", "method": "POST"}
        self.wfile.write(json.dumps(response).encode())