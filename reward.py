# reward.py

def calculate_cpu_penalty(cpu_usage):
    if cpu_usage <= 70:
        return 0
    else:
        # Linear penalty starting after 70% CPU
        return (cpu_usage - 70) * 2  # scaling factor (tune if needed)

def calculate_response_time_penalty(response_time):
    if response_time is None:
        return 1.0  # Max penalty if we can't get a response
    elif response_time <= 0.2:
        return 0  # Perfect, no penalty
    elif response_time <= 0.5:
        return (response_time - 0.2) * 10  # Gentle ramp between 200ms-500ms
    else:
        return (response_time - 0.5) * 20 + 3  # Steeper penalty after 500ms


def calculate_reward(cpu_usage, response_time, replicas):
    # Weights (tuneable if needed)
    alpha = 1.0  # CPU penalty weight
    beta = 5.0   # Response time penalty weight
    gamma = 0.5  # Replica penalty weight

    # CPU penalty
    cpu_penalty = calculate_cpu_penalty(cpu_usage)

    # Response time penalty
    response_penalty = calculate_response_time_penalty(response_time)

    # Replica penalty
    ideal_replicas = 2  # Ideal small app cluster size
    replica_penalty = max(0, replicas - ideal_replicas)

    # Final reward (lower total penalty → higher reward)
    reward = - (alpha * cpu_penalty + beta * response_penalty + gamma * replica_penalty)

    return reward
