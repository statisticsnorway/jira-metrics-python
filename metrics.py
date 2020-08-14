from os import getenv
import sys
import http.server
import signal
from livenessserver import LivenessServer
from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY
from jiracollector import JiraCollector

if __name__ == '__main__':
    
    REGISTRY.register(JiraCollector())
    
    # First we collect the environment variables that were set in either
    # the Dockerfile or the Kubernetes Pod specification.
    listen_port = int(getenv('LISTEN_PORT', 8090))
    prom_listen_port = int(getenv('PROM_LISTEN_PORT', 8080))

    # Let the Prometheus client export its metrics on a separate port.
    start_http_server(prom_listen_port)
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
