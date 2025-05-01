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

monitor = Monitor(PROMETHEUS_URL, DEPLOYMENT_NAME, SLEEP_TIME)
executor = Execute(NAMESPACE, DEPLOYMENT_NAME, MIN_REPLICAS, MAX_REPLICAS)
analyze = Analyze()

state_size = analyze.max_cpu_bucket * analyze.max_rt_bucket * analyze.max_pods
agent = QLearner(state_size=state_size)
agent.load("best_q_table.pkl")  # Load the trained Q-table

logger.info(f"Starting trained agent loop with namespace: {NAMESPACE}, deployment name: {DEPLOYMENT_NAME}")

try:
    while True:
        # Monitor -Get current metrics
        cpu = monitor.get_cpu_usage()
        rt = monitor.get_response_time()
        pods = monitor.get_pod_count()

        # Analyze -Discretize to state
        state_id = analyze.discretize(cpu, rt, pods)

        # Plan - Choose action
        action = agent.select_action(state_id)
    
        # Execute - Scale the deployment 
        executor.execute(action, pods)

        # Wait for system to stabilize
        time.sleep(SLEEP_TIME)

        logger.info(f"CPU: {cpu:.2f}%, RT: {rt:.2f}ms, Pods: {pods} → Action: {action}")


except KeyboardInterrupt:
    logger.info("Stopped Trained agent loop.")
