#!/usr/bin/env python3
"""Run a quick MQTT handler test."""
from src.protocols.mqtt_handler import MQTTHandler
from src.models.execution_models import ExecutionRequest

if __name__ == "__main__":
    handler = MQTTHandler()
    result = handler.execute(ExecutionRequest(payload_id="mqtt-demo", protocol="mqtt"))
    print(result)
