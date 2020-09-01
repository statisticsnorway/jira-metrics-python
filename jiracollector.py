import sys
import json
import google.auth
from google.cloud import secretmanager
from atlassian import Jira
from urllib.error import HTTPError
import configparser
import logging
logger = logging.getLogger()
config = configparser.ConfigParser()
config.read('metrics.ini')

class JiraCollector(object):
    def __init__(self,metricdescriptions):
        logger.info("Initialising JiraCollector")
        try:
            self.api_key = self.getApiKey()
            self.jira_conn = self.getJiraConnection()
        except:
            logger.exception("Error during initialisation of JiraCollector")
            self.api_key = None
            self.jira_conn = None
            raise

        self.result = {}
        self.metricdescriptions = metricdescriptions
        
    def getApiKey(self):
        logger.info('Getting API-key')
        try:
            # Get credenetials from Workload Identity
            credentials = google.auth.default()
            # Create client for secret manager
            client = secretmanager.SecretManagerServiceClient()
            # Fetch secret from secret manager
            name = client.secret_version_path(config.get('secrets','google_project_id'), config.get('secrets','name'), config.get('secrets','version'))
            response = client.access_secret_version(name)
            apiKey = response.payload.data
        except :
            logger.exception("Could not get apiKey for Google Secret Manager")
            apiKey = None
            raise
        return apiKey
    
    def getJiraConnection(self):
        logger.info('Connecting to Jira')
        try:
            jira_conn = Jira(
            url=config.get('jira','url'),
            username=config.get('jira','username'),
            password=self.api_key)
        except HTTPError:
            logger.exception("Error in connection with Jira")
            jira_conn = None
        return jira_conn

    def collect(self):
        logger.info("Creating jql from json")
        
        for metric in self.metricdescriptions['metrics']:
            for project in self.metricdescriptions['projects']:
                key = metric['name'] + "{project_name=\"" + project['name'] + "\"}"
                jql = "project = " + project['name'] + " AND " + metric['jql']
                value = str(self.queryJira(jql, metric['limit']))
                logger.debug("Got value: %s for metric: %s",value,key )
                self.result[key] = value
        return self.result

    def queryJira(self, jql, limitResults='None'):
        logger.debug('Running query : %s', jql)
        try:
            return self.jira_conn.jql(jql,limit=limitResults)['total']
        except HTTPError:
            logger.exception("Error in connection with Jira")        
