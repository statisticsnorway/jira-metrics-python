import asyncio
import logging
import json
import sys
from apscheduler.schedulers.background import BackgroundScheduler
from aiohttp import web
from jiracollector import JiraCollector
from datetime import datetime
from pythonjsonlogger import jsonlogger
import logging.config

logging.config.fileConfig('logging.config', defaults=None, disable_existing_loggers=True)
logger = logging.getLogger(__name__)

cachedMetrics = ""
serviceIsReady = False
def collectJiraMetrics():
    start = datetime.now()
    logger.info('Start collecting metrics...')
    global cachedMetrics
    global serviceIsReady
    
    jiraCollector = JiraCollector()
    metricsDict = jiraCollector.collect()
 
    logger.info("Converting metrics to strings")
    metricsStr = str(metricsDict)
    metricsStrReplaced = metricsStr[1:-1].replace("'", "").replace(':', '').replace(",", "\n").replace(" j", "j") + "\n"
    end = datetime.now()    

    # Logg and add metrics for this application
    logger.info("Adding metrics for this application")
    totalExecutionTime = abs((end - start).seconds)
    totalNumberOfMetrics = len(metricsDict)
    metricsStrReplaced = metricsStrReplaced+"jira_total_number_of_metrics "+str(totalNumberOfMetrics)+"\n"
    metricsStrReplaced = metricsStrReplaced+"jira_total_execution_time_seconds "+str(totalExecutionTime)+"\n"
    
    cachedMetrics = metricsStrReplaced
    logger.info("% d metrics collected OK in %d seconds",totalNumberOfMetrics,totalExecutionTime)
    

    serviceIsReady = True



def metrics(request):
    logger.info('Retrieving cached metrics')
    global cachedMetrics
    return web.Response(text=cachedMetrics)

def alive(request):
    return web.Response(status=200, text="OK")

def ready(request):
    global serviceIsReady
    if serviceIsReady:
        return web.Response(status=200, text="OK")
    else:
        return web.Response(status=503, text="Not ready yet")


if __name__ == "__main__":
    logger.info("Starting app")
    # Create a background thread to collect metrics in a "cache"
    scheduler = BackgroundScheduler()
    job = scheduler.add_job(collectJiraMetrics, 'interval', minutes=15, max_instances=1, next_run_time=datetime.now())
    scheduler.start()

    # Create a webapp to serve cached metrics on / endpoint
    app = web.Application()
    app.router.add_get('/', metrics)
    app.router.add_get('/health/ready', ready)
    app.router.add_get('/health/alive', alive)

    web.run_app(app)
