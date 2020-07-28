from atlassian import Jira
import prometheus_client as prom
import time

# TODO Get API-key for jira connection from Secret manager
api_key = "dummy-key"

def jira():
        jira = Jira(
                url='https://statistics-norway.atlassian.net',
                username='egk@ssb.no',
                password=api_key)
        JQL = 'project = BIP AND status IN ("To Do", "In Progress")'
        data = jira.jql(JQL)
        return data.get("total")

def process_request(t):
   time.sleep(t)

if __name__ == '__main__':

   gauge = prom.Gauge('jira_bip_active_issues', 'Backlog and active')
   prom.start_http_server(8080)

   while True:
       
       gauge.set(jira())
       time.sleep(10)
