from prometheus_client import Histogram
from django.urls import resolve
import time

request_latency = Histogram('django_request_latency_seconds', 'Request processing time in seconds', ['view_name'])