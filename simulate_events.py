#!/usr/bin/env python3
import asyncio
import socket
import uuid
import os
import logging

import paho.mqtt.client as mqtt
from async_helper import AsyncioHelper
from dotenv import load_dotenv

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
client_id = 'simulate_events_process/' + str(uuid.uuid4())
# topic = client_id
LOG.debug("Using client_id / topic: " + client_id)


class EventPublisher:
    def __init__(self, loop):
        self.loop = loop

    def on_disconnect(self, client, userdata, rc):
        self.disconnected.set_result(rc)

    async def main(self):
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
    LOG.debug("Starting")
    load_dotenv()
    event_loop = asyncio.get_event_loop()
    publisher = EventPublisher(event_loop)
    event_loop.run_until_complete(publisher.main())
    event_loop.close()
    LOG.debug("Finished")
