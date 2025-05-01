from flask import Flask
from prometheus_client import start_http_server, Summary
import time
import random

app = Flask(__name__)
REQUEST_LATENCY = Summary('flask_request_latency_seconds', 'Latency of / endpoint')


@app.route('/')
@REQUEST_LATENCY.time()
def index():
    start = time.time()
    x = 0
    for _ in range(2 * 10**6):
        x += 1
    duration = time.time() - start
    print(f"Request served in {duration:.3f} sec")
    return "Hello", 200

if __name__ == '__main__':
    start_http_server(8000)
    app.run(host='0.0.0.0', port=8080)
