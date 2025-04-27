## Kuberenetes Autoscaler RL Agent

This repository contains a reinforcement learning agent designed to optimize the autoscaling of Kubernetes clusters. 


## TODO

Generalize the k8s deployment.

Include all commands I've used so far to set up everything in a shell script.

```sh

kubectl create namespace default-scaling
kubectl create namespace rl-scaling


kubectl apply -n default-scaling -f k8s/flask-app.yaml
kubectl apply -n default-scaling -f k8s/flask-service.yaml

kubectl apply -n rl-scaling -f k8s/flask-app.yaml
kubectl apply -n rl-scaling -f k8s/flask-service.yaml
```