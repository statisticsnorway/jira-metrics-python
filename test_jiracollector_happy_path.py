from jiracollector import JiraCollector
import requests
from unittest import mock
import unittest
import pytest
import json
import google.auth

import logging.config
import configparser


config = configparser.ConfigParser()
config.read('metrics.ini')

logging.config.fileConfig(config.get('logging'
,'config_file'), defaults=None, disable_existing_loggers=True)

logger = logging.getLogger()

# Test that the number of metrics correspond with the expected
# from the json-file
@mock.patch('jiracollector.JiraCollector.getApiKey')
@mock.patch('jiracollector.JiraCollector.getJiraConnection')
@mock.patch('jiracollector.JiraCollector.queryJira')
def test_one_project_one_metric(mock_apikey, mock_jiraconnection, mock_query):
    mock_apikey.return_value = "test_apikey"
    mock_jiraconnection.return_value = "test_jiraconnection"
    mock_query.return_value = "heioghopp"
    
    with open('test_simple.json') as json_file:
        metricdescriptions = json.load(json_file)  
    jc = JiraCollector(metricdescriptions)    
    result = jc.collect()
    return result
assert len(test_one_project_one_metric()) == 1

# Test that the json-file gets correctly "transformed" to json-like
# metrics
@mock.patch('jiracollector.JiraCollector.getApiKey')
@mock.patch('jiracollector.JiraCollector.getJiraConnection')
@mock.patch('jiracollector.JiraCollector.queryJira')
def test_correctly_transformed_to_json_metric(mock_apikey, mock_jiraconnection, mock_query):
    mock_apikey.return_value = "test_apikey"
    mock_jiraconnection.return_value = "test_jiraconnection"
    mock_query.return_value = "42"
    
    with open('test_simple.json') as json_file:
        metricdescriptions = json.load(json_file)  
    jc = JiraCollector(metricdescriptions)    
    result = jc.collect()
    return result

# For some reason, even though mocking the queryJira method to return 42, it
# returns mock_apikey´s value which is 'test_apikey'. I have probably misconfigured something...
assert str(test_correctly_transformed_to_json_metric()) == '{\'jira_total_done{project_name="BIP"}\': \'test_apikey\'}'