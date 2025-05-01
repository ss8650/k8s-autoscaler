# qlearn.py

import numpy as np
import pickle
import random

class QLearner:
    def __init__(self, state_size, action_size=3, alpha=0.5, gamma=0.9, epsilon=0.2):
        self.q_table = np.zeros((state_size, action_size))
        self.alpha = alpha      # Learning rate
        self.gamma = gamma      # Discount factor
        self.epsilon = epsilon  # Exploration rate
        self.action_map = [-1, 0, 1]  # Map indices to real actions

    def select_action(self, state_id, valid_actions=None):
        if valid_actions is None:
            valid_actions = self.action_map
        
        valid_indices = [self.action_map.index(a) for a in valid_actions]
        q_values = self.q_table[state_id][valid_indices]

        if random.uniform(0, 1) < self.epsilon:
            return random.choice(valid_actions)
        else:
            best_index = valid_indices[np.argmax(q_values)]
            return self.action_map[best_index]

    def update(self, state_id, action, reward, next_state_id):
        action_idx = self.action_map.index(action)
        best_next_q = np.max(self.q_table[next_state_id])
        td_target = reward + self.gamma * best_next_q
        td_delta = td_target - self.q_table[state_id, action_idx]
        self.q_table[state_id, action_idx] += self.alpha * td_delta

    def save(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self.q_table, f)

    def load(self, path):
        with open(path, 'rb') as f:
            self.q_table = pickle.load(f)
