# execute.py

from kubernetes import client, config
import logging

logger = logging.getLogger(__name__)
class Execute:
    def __init__(self, namespace, deployment_name="flask-app", min_replicas=1, max_replicas=5):
        config.load_kube_config()
        self.apps_v1 = client.AppsV1Api()
        self.namespace = namespace
        self.deployment_name = deployment_name
        self.min_replicas = min_replicas
        self.max_replicas = max_replicas
        logger.info(f"Execute initialized with namespace: {self.namespace}, deployment name: {self.deployment_name}, min replicas: {self.min_replicas}, max replicas: {self.max_replicas}")

    def get_current_replicas(self):
        deployment = self.apps_v1.read_namespaced_deployment(
            name=self.deployment_name, namespace=self.namespace
        )
        return deployment.spec.replicas

    def scale(self, action):
        current = self.get_current_replicas()
        new_count = current + action
        new_count = max(self.min_replicas, min(self.max_replicas, new_count))
        if new_count == current:
            logger.info(f"No scaling needed. Current replicas: {current}")
            return current

        body = {'spec': {'replicas': new_count}}
        self.apps_v1.patch_namespaced_deployment_scale(
            name=self.deployment_name,
            namespace=self.namespace,
            body=body
        )
        logger.info(f"Scaled from {current} to {new_count} replicas")
        return new_count
