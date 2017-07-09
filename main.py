#!/usr/bin/env python3

from pynvml import *
from prometheus_client import start_http_server, Gauge
import random
import time


nvmlInit()

gpu_temp = Gauge('gpu_temperature', 'Temperature of the GPU', ['gpu_index', 'name'])
gpu_memory_free = Gauge('gpu_memory_free_bytes', 'Free memory', ['gpu_index', 'name'])
gpu_memory_total = Gauge('gpu_memory_total_bytes', 'Total memory', ['gpu_index', 'name'])
gpu_fan_speed = Gauge('gpu_fan_speed_percent', 'Fan speed in percent', ['gpu_index', 'name'])
gpu_power_usage = Gauge('gpu_power_usage_mw', 'Power usage in milliwatts, -1 if unsupported', ['gpu_index', 'name'])
gpu_last_reading = Gauge('gpu_last_reading_seconds', 'Last reading in seconds from epoch', ['gpu_index', 'name'])

device_count = nvmlDeviceGetCount()


is_power_reading_supported = True

if __name__ == '__main__':
    start_http_server(9080)
    while True:
        for i in range(device_count):
            handle = nvmlDeviceGetHandleByIndex(i)
            
            name = nvmlDeviceGetName(handle)
            info = nvmlDeviceGetMemoryInfo(handle)
            temp = nvmlDeviceGetTemperature(handle, NVML_TEMPERATURE_GPU)
            fan_speed = nvmlDeviceGetFanSpeed(handle)
            if is_power_reading_supported:
                try:
                    power_usage = nvmlDeviceGetPowerUsage(handle)
                    gpu_power_usage.labels(i, name).set(power_usage)
                except:
                    is_power_reading_supported = False
                    gpu_power_usage.labels(i, name).set(-1)
            else:
                gpu_power_usage.labels(i, name).set(-1)
                
            gpu_temp.labels(i, name).set(temp)
            gpu_memory_free.labels(i, name).set(info.free)
            gpu_memory_total.labels(i, name).set(info.total)
            gpu_fan_speed.labels(i, name).set(fan_speed)
            gpu_last_reading.labels(i, name).set(time.time())

        time.sleep(5)
