import metrics
import requests
from unittest import mock
import unittest
import pytest

def test_getApiKey():
    result = metrics.getApiKey()
    return result

assert test_getApiKey() != None

@mock.patch('metrics.getApiKey')
def test_getApiKeyMock(mock_apikey):
    mock_apikey.return_value = "test_apikey"
    result = metrics.getApiKey()
    return result

assert test_getApiKeyMock() == "test_apikey"

@mock.patch('metrics.getJiraConnection')
def test_getJiraConnectionMock(mock_jiraconnection):
    mock_jiraconnection.return_value = "test_jiraconnection"
    result = metrics.getJiraConnection()
    return result

assert test_getJiraConnectionMock() == "test_jiraconnection"

def test_json_client(httpserver):
    httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})
    assert requests.get(httpserver.url_for("/foobar")).json() == {'foo': 'bar'}
