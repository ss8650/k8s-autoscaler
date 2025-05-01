# locustfile_rl.py
from locust import HttpUser, task, between, LoadTestShape
import math

class SineWaveShape(LoadTestShape):
    """
    Users oscillate between 1 and 20 (instead of 50).
    Slower rise/fall to reduce burst stress.
    """
    max_users = 20
    cycle_time = 90  # longer cycle = gentler load changes

    def tick(self):
        run_time = self.get_run_time()
        users = int((self.max_users / 2) * (1 + math.sin(2 * math.pi * run_time / self.cycle_time)))
        return (users, 1)  # spawn 1 user per second


class TestUser(HttpUser):
    wait_time = between(2, 4)  # increase wait to space out requests

    @task
    def load(self):
        self.client.get("/")
