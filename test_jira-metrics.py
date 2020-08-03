import metrics
import requests
from unittest import mock

@mock.patch('metrics.getApiKey')
def test_getApiKey(mock_apikey):
    mock_apikey.return_value = "krabbegurgel"
    result = metrics.getApiKey()
    return result

assert test_getApiKey() == "krabbegurgel"

def test_json_client(httpserver):
    httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})
    assert requests.get(httpserver.url_for("/foobar")).json() == {'foo': 'bar'}
