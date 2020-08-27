import asyncio
import logging
import json
import sys
from apscheduler.schedulers.background import BackgroundScheduler
from aiohttp import web
from jiracollector import JiraCollector
from datetime import datetime

cachedMetrics = ""
serviceIsReady = False

def collectJiraMetrics():
    global cachedMetrics
    global serviceIsReady
    print("Running async")

    jiraCollector = JiraCollector()
    metricsDict = jiraCollector.collect()
    metricsStr = str(metricsDict)
    metricsStrReplaced = metricsStr[1:-1].replace("'", "").replace(':', '').replace(",", "\n").replace(" j", "j") + "\n"
    cachedMetrics = metricsStrReplaced
    serviceIsReady = True

def metrics(request):
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
    # Create a background thread to collect metrics in a "cache"
    scheduler = BackgroundScheduler()
    job = scheduler.add_job(collectJiraMetrics, 'interval', minutes=60, max_instances=1, next_run_time=datetime.now())
    scheduler.start()
    
    # Create a webapp to serve cached metrics on / endpoint
    app = web.Application()
    app.router.add_get('/', metrics)
    app.router.add_get('/health/ready', ready)
    app.router.add_get('/health/alive', alive)

    web.run_app(app)
