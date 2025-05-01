import logging
import requests


logger = logging.getLogger(__name__)

class Monitor:
    def __init__(self, prometheus_url="http://localhost:9090", deployment_name="flask-app", namespace="rl-scaling",sleep_time=30):
        self.prometheus_url = prometheus_url
        self.deployment_name = deployment_name
        self.namespace = namespace
        self.sleep_time = sleep_time
        logger.info(f"Monitor initialized with Prometheus URL: {self.prometheus_url} and deployment name: {self.deployment_name}")
    
    def query(self, promql):
        try:
            response = requests.get(f"{self.prometheus_url}/api/v1/query", params={"query": promql})
            result = response.json()["data"]["result"]
            return result
        except Exception as e:
            logger.error(f"Error querying Prometheus: {e}")
            return []
    
    def get_cpu_usage(self):
        query = f'sum(rate(container_cpu_usage_seconds_total{{namespace="{self.namespace}"}}[{self.sleep_time}s])) * 100'
        results = self.query(query)
        logger.info(f"CPU usage query: {query}")
        logger.info(f"CPU usage results: {results}")
        return sum(float(r["value"][1]) for r in results) if results else 0.0

    def get_response_time(self):
        query = f'rate(flask_request_latency_seconds_sum{{namespace="{self.namespace}"}}[{self.sleep_time}s]) / rate(flask_request_latency_seconds_count{{namespace="{self.namespace}"}}[{self.sleep_time}s])'
        results = self.query(query)
        if results:
            value = results[0]["value"][1]
            if value.lower() != "nan":
                return float(value) * 1000
        return 1000.0

    def get_pod_count(self):
        query = f'count(count_over_time(container_cpu_usage_seconds_total{{namespace="{self.namespace}", container!="POD"}}[{self.sleep_time}s]))'
        results = self.query(query)
        return int(float(results[0]["value"][1])) if results else 0
         