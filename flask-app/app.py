from flask import Flask
import time
import random

app = Flask(__name__)

@app.route('/')
def index():
    # Simulate some random processing time (realistic app behavior)
    time.sleep(random.uniform(0.05, 0.2))  # 50–200 ms delay
    return "Hello from the CPU-burner app!", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
