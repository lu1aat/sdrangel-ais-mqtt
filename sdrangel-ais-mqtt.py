#!/usr/bin/env python3

import socket
import paho.mqtt.client as mqtt
import logging
import json
import argparse
from typing import Dict, Optional, List
import select

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AISMQTTPublisher:
    MQTT_BROKER = "localhost"
    MQTT_PORT = 1883
    MQTT_TOPIC = "ais/data"
    
    # Default AIS server configuration
    DEFAULT_AIS_SERVERS = [
        {"name": "node-montevideo-1", "host": "127.0.0.1", "port": 9999}
    ]

    def __init__(self, ais_servers: List[Dict] = None):
        self.udp_sockets = {}
        self.mqtt_client = None
        self.ais_servers = ais_servers or self.DEFAULT_AIS_SERVERS

    def on_disconnect(self, client, userdata, rc):
        """Callback for when the client disconnects from the broker"""
        if rc != 0:
            logger.error(f"Lost connection to MQTT broker (code: {rc})")
        else:
            logger.info("Disconnected from MQTT broker")

    def setup_udp_sockets(self):
        """Set up UDP sockets for receiving AIS data from multiple servers"""
        try:
            for server in self.ais_servers:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.bind((server['host'], server['port']))
                self.udp_sockets[server['name']] = sock
                logger.info(f"UDP socket bound to {server['host']}:{server['port']} for node {server['name']}")
        except Exception as e:
            logger.error(f"Failed to set up UDP sockets: {e}")
            raise

    def setup_mqtt(self):
        """Set up MQTT client"""
        try:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.on_disconnect = self.on_disconnect
            self.mqtt_client.connect(self.MQTT_BROKER, self.MQTT_PORT)
            self.mqtt_client.loop_start()  # Start the network loop in a background thread
            logger.info(f"Connected to MQTT broker at {self.MQTT_BROKER}:{self.MQTT_PORT}")
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise

    def process_message(self, data, node_name: str):
        """Process AIS message and publish to MQTT"""
        try:
            logger.debug(f"Received from {node_name}: {data}")
            message = dict()
            message['raw'] = data.decode('utf-8').strip()
            message['node'] = node_name
            mqtt_payload = json.dumps(message)
            self.mqtt_client.publish(self.MQTT_TOPIC, mqtt_payload)
            logger.debug(f"Published: {mqtt_payload}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    def run(self):
        """Main loop for receiving and processing messages"""
        try:
            self.setup_udp_sockets()
            self.setup_mqtt()

            logger.info("Connected to AIS NMEA servers...")

            while True:
                try:
                    # Use select to monitor multiple sockets
                    readable, _, _ = select.select(list(self.udp_sockets.values()), [], [])
                    for sock in readable:
                        data, addr = sock.recvfrom(1024)
                        # Find the node name for this socket
                        node_name = next(name for name, s in self.udp_sockets.items() if s == sock)
                        self.process_message(data, node_name)
                except Exception as e:
                    logger.error(f"Error in main loop: {e}")
                    continue

        except KeyboardInterrupt:
            logger.info("Shutting down...")
        finally:
            for sock in self.udp_sockets.values():
                sock.close()
            if self.mqtt_client:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AIS UDP to MQTT publisher")
    parser.add_argument("--mqtt-host", default="localhost", help="MQTT broker hostname or IP")
    parser.add_argument("--mqtt-topic", default="ais/data", help="MQTT topic to publish AIS data")
    parser.add_argument("--ais-servers", type=json.loads, default=None,
                      help='JSON array of AIS servers, e.g. [{"name":"node1","host":"127.0.0.1","port":9999}]')
    args = parser.parse_args()

    AISMQTTPublisher.MQTT_BROKER = args.mqtt_host
    AISMQTTPublisher.MQTT_TOPIC = args.mqtt_topic

    publisher = AISMQTTPublisher(ais_servers=args.ais_servers)
    publisher.run()