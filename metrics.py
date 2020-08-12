from os import getenv
import sys
import json
import google.auth
from google.cloud import secretmanager
import google.auth
from google.cloud import secretmanager
import http.server
import signal
from atlassian import Jira
import prometheus_client as prom
from livenessserver import LivenessServer

def getApiKey():
    try:
        # Get credenetials from Workload Identity
        credentials = google.auth.default()
    except:
        print("Could not get credentials from Google Cloud", file=sys.stderr)
    try:
        # Create client for secret manager
        client = secretmanager.SecretManagerServiceClient()
        # Fetch secret from secret manager
        name = client.secret_version_path('ssb-team-stratus', 'jira-api-key', 'latest')
        response = client.access_secret_version(name)
        apiKey = response.payload.data
    except:
        print("Could not get apiKey for Google Secret Manager", file=sys.stderr)
    return apiKey

apikey = getApiKey()

def getJiraConnection():
    try:
        jira_conn = Jira(
        url='https://statistics-norway.atlassian.net',
        username='egk@ssb.no',
        password=apiKey)
        return jira_conn
    except HTTPError:
        print("Error in connection with Jira", file=sys.stderr)

jira_conn = getJiraConnection()

def queryJira(jql, limitResults='None'):
    return jira_conn.jql(jql,limit=limitResults)['total']

# Read metric descriptions from file
with open('metricdescriptions.json') as json_file:
    metricdescriptions = json.load(json_file)

for metric in metricdescriptions:
    result = {}
    if metric['type'].lower() == "gauge":
        result[metric['metric name']] = prom.Gauge(metric['metric name'], metric['description'])
    result[metric['metric name']].set(queryJira(metric['jql'], metric['limit']))

if __name__ == '__main__':
    # First we collect the environment variables that were set in either
    # the Dockerfile or the Kubernetes Pod specification.
    listen_port = int(getenv('LISTEN_PORT', 8090))
    prom_listen_port = int(getenv('PROM_LISTEN_PORT', 8080))

    # Let the Prometheus client export its metrics on a separate port.
    prom.start_http_server(prom_listen_port)
    # Let our web application run and listen on the specified port.
    httpd = http.server.HTTPServer(('localhost', listen_port), LivenessServer)
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
