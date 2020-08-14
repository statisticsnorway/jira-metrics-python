import jiracollector
import requests
from unittest import mock
import unittest
import pytest

@mock.patch('jiracollector.JiraCollector.getApiKey')
def test_getApiKeyMock(mock_apikey):
    mock_apikey.return_value = "test_apikey"
    result = jiracollector.JiraCollector.getApiKey()
    return result

assert test_getApiKeyMock() == "test_apikey"

@mock.patch('jiracollector.JiraCollector.getJiraConnection')
def test_getJiraConnectionMock(mock_jiraconnection):
    mock_jiraconnection.return_value = "test_jiraconnection"
    result = jiracollector.JiraCollector.getJiraConnection()
    return result

assert test_getJiraConnectionMock() == "test_jiraconnection"

def test_json_client(httpserver):
    httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})
    assert requests.get(httpserver.url_for("/foobar")).json() == {'foo': 'bar'}
