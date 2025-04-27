# run.py

import time
import pandas as pd
import requests

from kubernetes_api import get_cpu_usage, get_current_replicas, scale_replicas
from agent import RLAgent
from reward import calculate_reward

NAMESPACE = "rl-scaling"
SERVICE_URL = "http://127.0.0.1:37889/"  # Adjust this to your actual Minikube tunneled URL
SLEEP_TIME = 10  # seconds between agent actions

agent = RLAgent()

# Setup logging
columns = ['timestamp', 'cpu_usage_percent', 'replicas', 'response_time_sec', 'action', 'reward']
log = []

print(f"Starting RL agent monitoring in namespace: {NAMESPACE}")

def measure_response_time(url):
    try:
        start = time.time()
        response = requests.get(url, timeout=2)
        end = time.time()
        if response.status_code == 200:
            latency = end - start
            return latency
        else:
            return None
    except:
        return None

try:
    while True:
        timestamp = pd.Timestamp.now()

        cpu_usage = get_cpu_usage(NAMESPACE)
        replicas = get_current_replicas(NAMESPACE)
        response_time = measure_response_time(SERVICE_URL)

        # Agent chooses action
        state = agent.discretize_state(cpu_usage, response_time, replicas)
        action = agent.select_action(state)

        # Calculate new replicas
        new_replicas = agent.scale_replicas(replicas, action)

        # Scale only if needed
        if new_replicas != replicas:
            scale_replicas(NAMESPACE, new_replicas)

        # Allow cluster to stabilize
        time.sleep(SLEEP_TIME)

        # Observe next state
        next_cpu_usage = get_cpu_usage(NAMESPACE)
        next_replicas = get_current_replicas(NAMESPACE)
        next_response_time = measure_response_time(SERVICE_URL)

        next_state = agent.discretize_state(next_cpu_usage, next_response_time, next_replicas)

        # Calculate reward
        reward = calculate_reward(next_cpu_usage, next_response_time, next_replicas)

        # Update agent
        agent.update_q_table(state, action, reward, next_state)

        # Log everything
        log.append([timestamp, cpu_usage, replicas, response_time, action, reward])
        print(f"[{timestamp}] CPU: {cpu_usage:.2f}% | Replicas: {replicas} | Response Time: {response_time:.3f} sec | Action: {action} | Reward: {reward:.2f}")

        # Save Q-table every 10 steps
        if len(log) % 10 == 0:
            agent.save("q_table.pkl")

except KeyboardInterrupt:
    print("\nStopping RL agent and saving logs...")

    df = pd.DataFrame(log, columns=columns)
    df.to_csv("metrics_log_rl_agent.csv", index=False)
    print("Saved metrics_log_rl_agent.csv and q_table.pkl")
