# agent.py

import random
import numpy as np
import pickle

class RLAgent:
    def __init__(self, alpha=0.5, gamma=0.9, epsilon=0.2, min_replicas=1, max_replicas=5):
        self.q_table = {}  # Q-values: {state: {action: value}}
        self.alpha = alpha  # Learning rate
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.actions = [0, 1, 2]  # 0 = scale_down, 1 = no_change, 2 = scale_up
        self.min_replicas = min_replicas
        self.max_replicas = max_replicas

    def discretize_state(self, cpu_usage, response_time, replicas):
        cpu_bucket = self.bucket_cpu(cpu_usage)
        response_bucket = self.bucket_response_time(response_time)
        replicas = int(replicas)  # Keep replicas as integer
        return (cpu_bucket, response_bucket, replicas)

    def bucket_cpu(self, cpu_usage):
        if cpu_usage < 20:
            return 0
        elif cpu_usage < 50:
            return 1
        elif cpu_usage < 80:
            return 2
        else:
            return 3

    def bucket_response_time(self, response_time):
        if response_time is None:
            return 2  # Assume worst if no response
        elif response_time < 0.2:
            return 0
        elif response_time < 0.5:
            return 1
        else:
            return 2

    def select_action(self, state):
        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in self.actions}

        if random.uniform(0, 1) < self.epsilon:
            return random.choice(self.actions)  # Explore
        else:
            return max(self.q_table[state], key=self.q_table[state].get)  # Exploit

    def update_q_table(self, state, action, reward, next_state):
        if state not in self.q_table:
            self.q_table[state] = {a: 0.0 for a in self.actions}
        if next_state not in self.q_table:
            self.q_table[next_state] = {a: 0.0 for a in self.actions}

        best_next_action = max(self.q_table[next_state], key=self.q_table[next_state].get)
        td_target = reward + self.gamma * self.q_table[next_state][best_next_action]
        td_delta = td_target - self.q_table[state][action]

        self.q_table[state][action] += self.alpha * td_delta

    def scale_replicas(self, current_replicas, action):
        if action == 0:  # scale down
            new_replicas = current_replicas - 1
        elif action == 1:  # no change
            new_replicas = current_replicas
        elif action == 2:  # scale up
            new_replicas = current_replicas + 1
        else:
            new_replicas = current_replicas  # Fallback
        
        # Clamp between min and max replicas
        new_replicas = max(self.min_replicas, min(self.max_replicas, new_replicas))
        return new_replicas

    def save(self, filepath):
        with open(filepath, 'wb') as f:
            pickle.dump(self.q_table, f)

    def load(self, filepath):
        with open(filepath, 'rb') as f:
            self.q_table = pickle.load(f)

