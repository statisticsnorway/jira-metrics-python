# jira-metrics-python
Python application to expose metrics from Jira to Prometheus

The application utilizes Workload Indentity to authorize itself and fetch the necessary API key to contact Jira. The Workload Identity service account is given read access to the necessary secret in Secret Manager.
