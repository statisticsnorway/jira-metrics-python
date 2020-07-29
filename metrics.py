from atlassian import Jira
import prometheus_client as prom
from google.cloud import secretmanager
import google.auth
import time

# Get credenetials from Workload Identity
credentials = google.auth.default()

# Create client for secret manager
client = secretmanager.SecretManagerServiceClient()
# Fetch secret from secret manager
name = client.secret_version_path('ssb-team-stratus', 'jira-api-key', 'latest')
api_key = client.access_secret_version(name)
if api_key:
  print("The String is not Empty")
else:
  print("The String is Empty")

# def jira():
#         jira = Jira(
#                 url='https://statistics-norway.atlassian.net',
#                 username='egk@ssb.no',
#                 password=api_key)
#         JQL = 'project = BIP AND status IN ("To Do", "In Progress")'
#         data = jira.jql(JQL)
#         return data.get("total")

def jira():
        return 82

def process_request(t):
   time.sleep(t)

if __name__ == '__main__':

   gauge = prom.Gauge('jira_bip_active_issues', 'Backlog and active')
   prom.start_http_server(8080)

   while True:
       
       gauge.set(jira())
       time.sleep(10)
