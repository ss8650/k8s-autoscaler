import pickle

# Load Q-table
with open('q_table.pkl', 'rb') as f:
    q_table = pickle.load(f)

# Inspect keys (states) and actions
print(f"Total states learned: {len(q_table)}\n")

for state, actions in q_table.items():
    print(f"State: {state}")
    for action, value in actions.items():
        print(f"  Action {action} → Q-value: {value:.4f}")
    print()
