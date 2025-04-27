# run.py

import time
import pandas as pd
from kubernetes_api import get_cpu_usage, get_current_replicas
import requests

def measure_response_time(url):
    try:
        start = time.time()
        response = requests.get(url, timeout=2)
        latency = time.time() - start
        if response.status_code == 200:
            return latency
        else:
            print(f"Error: {response.status_code}")
            return None  # or a big penalty
    except:
        print("Request failed")
        return None  # if server error or timeout

NAMESPACE = "default-scaling"
SERVICE_URL = "http://127.0.0.1:35863/"
SLEEP_TIME = 10  # seconds between polls

# Set up simple logging
columns = ['timestamp', 'cpu_usage_percent', 'replicas', 'response_time_sec']
log = []

print(f"Monitoring namespace: {NAMESPACE}")

try:
    while True:
        timestamp = pd.Timestamp.now()
        cpu_usage = get_cpu_usage(NAMESPACE)
        replicas = get_current_replicas(NAMESPACE)
        response_time = measure_response_time(SERVICE_URL)

        print(f"[{timestamp}] CPU: {cpu_usage:.2f}% | Replicas: {replicas} | Response Time: {response_time:.3f} sec")

        log.append([timestamp, cpu_usage, replicas, response_time])


        time.sleep(SLEEP_TIME)

except KeyboardInterrupt:
    print("\nStopping monitor and saving log...")

    df = pd.DataFrame(log, columns=columns)
    df.to_csv("metrics_log.csv", index=False)
    print("Saved metrics_log.csv")
