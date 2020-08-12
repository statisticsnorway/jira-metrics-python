import http.server
import sys
import threading
import os
import json
import time
import os

class LivenessServer(http.server.BaseHTTPRequestHandler):
    ready = True

    def do_GET(s):
        if s.path == '/health/alive':
            s.liveness_check()
        elif s.path == '/health/ready':
            s.readiness_check()

    def liveness_check(s):
        s.send_response(200)
        s.send_header('Content-Type', 'text/html')
        s.end_headers()
        s.wfile.write(b'''Ok.''')

    def readiness_check(s):
        if s.ready:
            s.send_response(200)
            s.send_header('Content-Type', 'text/plain')
            s.end_headers()
            s.wfile.write(b'''Ok.''')
        else:
            # The actual response does not really matter, as long as it's not
            # a HTTP 200 status.
            s.send_response(503)
            s.send_header('Content-Type', 'text/plain')
            s.end_headers()
            s.wfile.write(b'''Not ready yet.''')
