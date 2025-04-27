# kubernetes_api.py

from kubernetes import client, config
import subprocess

# Load kubeconfig (for Minikube/local cluster)
config.load_kube_config()

# Kubernetes API clients
apps_v1 = client.AppsV1Api()
core_v1 = client.CoreV1Api()
custom_api = client.CustomObjectsApi()

def get_current_replicas(namespace, deployment_name="flask-cpu-burner"):
    deployment = apps_v1.read_namespaced_deployment(deployment_name, namespace)
    return deployment.status.replicas or 0

def scale_replicas(namespace, new_replica_count, deployment_name="flask-cpu-burner"):
    body = {
        'spec': {
            'replicas': new_replica_count
        }
    }
    apps_v1.patch_namespaced_deployment_scale(
        name=deployment_name,
        namespace=namespace,
        body=body
    )
    print(f"Scaled {deployment_name} to {new_replica_count} replicas in {namespace}")

def get_cpu_usage(namespace, deployment_label="app=flask-cpu-burner"):
    # Use kubectl top pods because Metrics API is not fully in client-python
    cmd = f"kubectl top pods -n {namespace} --selector={deployment_label} --no-headers"
    output = subprocess.check_output(cmd, shell=True).decode().strip()
    
    if not output:
        return 0.0

    # Example line: cpu-burner-xxxxxxxx  120m  10Mi
    lines = output.split('\n')
    cpu_millicores = 0
    for line in lines:
        parts = line.split()
        cpu = parts[1]  # CPU usage like '120m'
        if cpu.endswith('m'):
            cpu_millicores += int(cpu[:-1])
        else:
            cpu_millicores += int(cpu) * 1000

    # Convert to percentage assuming 1 core = 1000m
    # (you can refine based on limits/requests if needed)
    return cpu_millicores / 1000.0 * 100  # as percentage
