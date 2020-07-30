from atlassian import Jira
import prometheus_client as prom
from google.cloud import secretmanager
import google.auth
import http.server
import signal
import sys
import threading
import os
import json
import time

# Get credenetials from Workload Identity
credentials = google.auth.default()

# Create client for secret manager
client = secretmanager.SecretManagerServiceClient()

# Fetch secret from secret manager
name = client.secret_version_path('ssb-team-stratus', 'jira-api-key', 'latest')
response = client.access_secret_version(name)
api_key = response.payload.data


def jira():
    jira_conn = Jira(
        url='https://statistics-norway.atlassian.net',
        username='egk@ssb.no',
        password=api_key)
    jql = 'project = BIP AND status IN ("To Do", "In Progress")'
    data = jira_conn.jql(jql)
    return data.get("total")


class MyWebpage(http.server.BaseHTTPRequestHandler):
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


if __name__ == '__main__':
    # First we collect the environment variables that were set in either
    # the Dockerfile or the Kubernetes Pod specification.
    listen_port = int(os.getenv('LISTEN_PORT', 8090))
    prom_listen_port = int(os.getenv('PROM_LISTEN_PORT', 8080))

    gauge = prom.Gauge('jira_bip_active_issues', 'Backlog and active')
    gauge.set(jira())
    # Let the Prometheus client export its metrics on a separate port.
    prom.start_http_server(prom_listen_port)
    # Let our web application run and listen on the specified port.
    httpd = http.server.HTTPServer(('localhost', listen_port), MyWebpage)
    # Make sure you have the webserver signal when it's done.
    httpd.ready = True

    # Simple handler function to show that we we're handling the SIGTERM
    def do_shutdown(signum, frame):
        global httpd

        log = {'jira-metrics': {'message': 'Graceful shutdown.'}}
        print(json.dumps(log))
        threading.Thread(target=httpd.shutdown).start()
        sys.exit(0)

    # We catch the SIGTERM signal here and shut down the HTTPServer
    signal.signal(signal.SIGTERM, do_shutdown)

    # Forever serve requests. Or at least until we receive the proper signal.
    httpd.serve_forever()
