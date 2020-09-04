from jiracollector import JiraCollector
import requests
from unittest import mock
import unittest
import pytest
import json
import google.auth
from google.cloud import secretmanager
from atlassian import Jira
from urllib.error import HTTPError

import logging.config
import configparser


config = configparser.ConfigParser()
config.read('metrics.ini')

logging.config.fileConfig(config.get('logging'
,'config_file'), defaults=None, disable_existing_loggers=True)
logger = logging.getLogger()

# Tests that if an Error is raised when obtaining the api-key,
# the init method also raises an Error
@mock.patch('google.auth.default', side_effect=mock.Mock(side_effect=Exception('Test')),autospec=True)
def test_that_getApiKey_raises_exception(mock_google_api):
    with pytest.raises(Exception):
        assert JiraCollector("NA")

# Mocks everything up to the point where the file is loaded
# and tests that a non-existing file leads to an Exception
@mock.patch('jiracollector.JiraCollector.getApiKey')
@mock.patch('jiracollector.JiraCollector.getJiraConnection')
def test_metricsdescriptions_file_does_not_exist(mock_apikey, mock_jiraconnection):
    mock_apikey.return_value = "test_apikey"
    mock_jiraconnection.return_value = "test_jiraconnection"
    with pytest.raises(FileNotFoundError):
        assert JiraCollector("filedoesnotexist.json")

# Creates an empty file ,mocks everything up to the point where the file is
# loaded and tests that an Error is raised
@mock.patch('jiracollector.JiraCollector.getApiKey')
@mock.patch('jiracollector.JiraCollector.getJiraConnection')
def test_open_empty_metricsdescriptions_file(mock_apikey, mock_jiraconnection):
    mock_apikey.return_value = "test_apikey"
    mock_jiraconnection.return_value = "test_jiraconnection"
    open("empty_file.json", 'a').close()
    with pytest.raises(FileNotFoundError):
        assert JiraCollector("empty_file.json")

# Tests that the init method raises an Error if getting Jira connection
# fails
@mock.patch('jiracollector.JiraCollector.getApiKey')
@mock.patch('atlassian.Jira.__init__', side_effect=mock.Mock(side_effect=HTTPError('http://example.com', 500, 'Internal Error', {}, None)),autospec=True)
def test_that_getJiraConnection_raises_exception(mock_apikey, mock_jiraconnection):
    mock_apikey.return_value = "test_apikey"
    with pytest.raises(HTTPError):
        assert JiraCollector("NA")
