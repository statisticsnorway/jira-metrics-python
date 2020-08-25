import sys
import json
import google.auth
from google.cloud import secretmanager
from atlassian import Jira
from urllib.error import HTTPError

class JiraCollector(object):
    def __init__(self):
        self.api_key = self.getApiKey()
        self.jira_conn = self.getJiraConnection()
        self.result = {}

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
            for project in metricdescriptions['projects']:
                key = metric['name'] + "{project_name=\"" + project['name'] + "\"}"
                jql = "project = " + project['name'] + " AND " + metric['jql']
                value = "\'" + str(self.queryJira(jql, metric['limit'])) + ".0\'"
                self.result[key] = value
        return self.result
