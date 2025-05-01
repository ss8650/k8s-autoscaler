import time
from monitor import Monitor
from execute import Execute
from analyze import Analyze
from q_learner import QLearner
from config import *
from utils.setup_logging import configure_logging
import logging


configure_logging()
logger = logging.getLogger(__name__)

monitor = Monitor(PROMETHEUS_URL, DEPLOYMENT_NAME, NAMESPACE,SLEEP_TIME)
executor = Execute(NAMESPACE, DEPLOYMENT_NAME, MIN_REPLICAS, MAX_REPLICAS)
analyze = Analyze()

state_size = (analyze.max_cpu_bucket + 1)* (analyze.max_rt_bucket + 1) * analyze.max_pods
agent = QLearner(state_size=state_size)

logger.info(f"Starting training loop with namespace: {NAMESPACE}, deployment name: {DEPLOYMENT_NAME}")
executor.scale(-10)  # Ensure at least one pod is running

try:
    while True:
        # Monitor -Get current metrics
        cpu = monitor.get_cpu_usage()
        rt = monitor.get_response_time()
        pods = monitor.get_pod_count()
        logger.info(f"Current metrics - CPU: {cpu:.2f}%, RT: {rt:.2f}ms, Pods: {pods}")

        # Analyze -Discretize to state
        state_id = analyze.discretize(cpu, rt, pods)
        valid_actions = [-1, 0, 1]
        if pods == 1:
            valid_actions.remove(-1)
        elif pods == analyze.max_pods:
            valid_actions.remove(1)

        # Plan - Choose action
        action = agent.select_action(state_id, valid_actions)
        logger.info(f"Selected action: {action}")
    
        # Execute - Scale the deployment 
        new_pods = executor.scale(action)

        # Wait for system to stabilize
        time.sleep(SLEEP_TIME)

        # Get new state and reward
        next_cpu = monitor.get_cpu_usage()
        next_rt = monitor.get_response_time()
        next_pods = monitor.get_pod_count()

        next_state_id = analyze.discretize(next_cpu, next_rt, next_pods)
        reward = analyze.get_reward(next_cpu, next_rt, next_pods, pods)

        # Q-learning update
        agent.update(state_id, action, reward, next_state_id)

        logger.info(f"CPU: {cpu:.2f}%, RT: {rt:.2f}ms, Pods: {pods} -> Action: {action}, Reward: {reward:.2f}")


except KeyboardInterrupt:
    logger.info("Training interrupted. Saving Q-table.")
    agent.save("q_table.pkl")
