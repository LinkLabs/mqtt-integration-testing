#!/usr/bin/env python3
import argparse
import asyncio
from dataclasses import dataclass
import uuid
import logging
import os
import socket

import paho.mqtt.client as mqtt
from async_helper import AsyncioHelper
from dotenv import load_dotenv

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
client_id = 'simulate_events_process/' + str(uuid.uuid4())


@dataclass
class MqttHistory:
    mqttHistoryId: int
    nodeAddress: int
    organizationId: str
    siteId: str
    areaId: str
    zoneId: str
    topic: str
    payload: str
    eventId: str
    eventTime: str
    processedTime: str


class EventPublisher:
    def __init__(self, loop):
        self.loop = loop

    def on_disconnect(self, client, userdata, rc):
        self.disconnected.set_result(rc)

    async def main(self, filename: str, msg_delay: int = 0):
        self.disconnected = self.loop.create_future()
        self.got_message = None

        self.client = mqtt.Client(client_id=client_id)
        self.client.username_pw_set(os.getenv("MQTT_USER", 'test-user'), os.getenv('MQTT_PASSWORD'))
        self.client.on_disconnect = self.on_disconnect

        aioh = AsyncioHelper(self.loop, self.client)

        self.client.connect(os.getenv('MQTT_HOST', 'localhost'), 1883, 60)
        self.client.socket().setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)

        for c in range(3):
            await asyncio.sleep(5)
            LOG.debug("Publishing")
            self.got_message = self.loop.create_future()
            self.client.publish(topic, b'Hello' * 40000, qos=1)
            msg = await self.got_message
            LOG.debug("Got response with {} bytes".format(len(msg)))
            self.got_message = None

        self.client.disconnect()
        LOG.debug("Disconnected: {}".format(await self.disconnected))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('json_data_filename', type=str, help='file name of the json file containing data to publish')
    parser.add_argument('--msg_delay', type=int, default=0, help='The amount of delay between messages (default: 0)')
    args = parser.parse_args()

    data_filename = args.get('json_data_filename')
    delay = args.get('msg_delay')

    LOG.debug("Starting")
    load_dotenv()
    event_loop = asyncio.get_event_loop()
    publisher = EventPublisher(event_loop)
    event_loop.run_until_complete(publisher.main(data_filename, delay))
    event_loop.close()
    LOG.debug("Finished")
