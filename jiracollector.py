import sys
import json
import google.auth
from google.cloud import secretmanager
from atlassian import Jira
from prometheus_client.core import GaugeMetricFamily
from urllib.error import HTTPError

class JiraCollector(object):
    def __init__(self):
        self.labels = ['project_name' ]
        self.api_key = self.getApiKey()
        self.jira_conn = self.getJiraConnection()

    def getApiKey(self):
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
            apiKey = None
        return apiKey
    
    def getJiraConnection(self):
        try:
            jira_conn = Jira(
            url='https://statistics-norway.atlassian.net',
            username='egk@ssb.no',
            password=self.api_key)
        except HTTPError:
            print("Error in connection with Jira", file=sys.stderr)
            jira_conn = None
        return jira_conn

    def queryJira(self, jql, limitResults='None'):
        try:
            return self.jira_conn.jql(jql,limit=limitResults)['total']
        except HTTPError:
            print("Error in connection with Jira", file=sys.stderr)

    def collect(self):
        with open('metricdescriptions.json') as json_file:
            metricdescriptions = json.load(json_file)
        for metric in metricdescriptions['metrics']:
            metric['name'] = GaugeMetricFamily(metric['name'], metric['description'], labels=self.labels)
            for project in metricdescriptions['projects']:
                jql = "project = " + project['name'] + " AND " + metric['jql']
                value = self.queryJira(jql, metric['limit'])
                metric['name'].add_metric([project['name']], value)
            yield metric['name']