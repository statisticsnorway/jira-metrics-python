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

@mock.patch('jiracollector.JiraCollector.queryJira')
@mock.patch('jiracollector.JiraCollector.getApiKey', mock.MagicMock(return_value="test_jira_connection"))
@mock.patch('jiracollector.JiraCollector.getJiraConnection', mock.MagicMock(return_value="test_apikey"))
def test_collect_metrics_converts_jsonfile_to_correct_jql(mock_query_jira):
    mock_query_jira.return_value ="42"
    
    jc = JiraCollector("simple_test.json")    
    
    result = jc.collect()
    assert mock_query_jira.call_count == 2
    mock_query_jira.assert_any_call('project = BIP AND status IN ("10002")', 0)
    mock_query_jira.assert_any_call('project = DAPLA AND status IN ("10002")', 0)

@mock.patch('jiracollector.JiraCollector.queryJira')
@mock.patch('jiracollector.JiraCollector.getApiKey', mock.MagicMock(return_value="test_jira_connection"))
@mock.patch('jiracollector.JiraCollector.getJiraConnection', mock.MagicMock(return_value="test_apikey"))
def test_collect_metrics_converts_jql_results_to_correct_dictionary(mock_query_jira):
    mock_query_jira.return_value ="42"
    
    jc = JiraCollector("simple_test.json")    
    
    result = jc.collect()
    expectedMetricsDict ={
        "jira_total_done{project_name=\"BIP\"}":"42",
        "jira_total_done{project_name=\"DAPLA\"}":"42"
    }
    assert result ==  expectedMetricsDict
