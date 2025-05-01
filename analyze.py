class Analyze:
    def __init__(self):
        self.cpu_bucket_size = 15  # percentage
        self.rt_bucket_size = 250  # milliseconds
        self.max_cpu_bucket = 6    # up to 90%
        self.max_rt_bucket = 3     # up to 750ms
        self.max_pods = 5
        self.ideal_cpu_bucket = 4  # 60-75%
        self.ideal_rt_bucket = 1 # 0-250ms
        self.rt_penalty_weight = 0.5
        self.cpu_penalty_weight = 0.3
        self.pod_penalty_weight = 0.2
    
    def get_cpu_bucket(self, cpu_utilization):
        if cpu_utilization is None:
            return self.max_cpu_bucket
        return min(int(cpu_utilization // self.cpu_bucket_size), self.max_cpu_bucket)

    def get_rt_bucket(self, response_time):
        if response_time is None:
            return self.max_rt_bucket
        return min(int(response_time // self.rt_bucket_size), self.max_rt_bucket)

    def get_pod_index(self, pod_count):
        if pod_count is None:
            return self.max_pods - 1
        return min(pod_count - 1, self.max_pods - 1)

    def discretize(self, cpu_utilization, response_time, pod_count):
        cpu_bucket = self.get_cpu_bucket(cpu_utilization)
        rt_bucket = self.get_rt_bucket(response_time)
        pod_index = self.get_pod_index(pod_count)
        state_id = cpu_bucket + rt_bucket * (self.max_cpu_bucket + 1) + pod_index * (self.max_cpu_bucket + 1) * (self.max_rt_bucket + 1)
        return state_id
    
    def get_reward(self, cpu_utilization, response_time, pod_count, current_pod_count):
        cpu_bucket = self.get_cpu_bucket(cpu_utilization)
        rt_bucket = self.get_rt_bucket(response_time)
        pod_index = self.get_pod_index(pod_count)
        cpu_penalty = abs(cpu_bucket - self.ideal_cpu_bucket) * self.cpu_penalty_weight
        rt_penalty = abs(rt_bucket - self.ideal_rt_bucket) * self.rt_penalty_weight
        pod_penalty = abs(pod_index - self.get_pod_index(current_pod_count)) * self.pod_penalty_weight
        reward = -(cpu_penalty + rt_penalty + pod_penalty)
        return reward
