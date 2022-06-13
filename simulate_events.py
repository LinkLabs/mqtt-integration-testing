#!/usr/bin/env python3
import argparse
import asyncio
from dataclasses import dataclass
import uuid
import logging
import json
import os
import socket
from typing import List

import paho.mqtt.client as mqtt
from async_helper import AsyncioHelper
from dotenv import load_dotenv

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
CLIENT_ID = 'simulate_events_process/' + str(uuid.uuid4())


@dataclass
class QueryResponse:
    moreRecordsExist: bool
    currentPage: int
    maxPage: int
    results: List[dict]


@dataclass
class MqttHistory:
    uuid: str
    time: str
    topic: str
    payload: str
    organizationId: str
    siteId: str


def load_json(path: str) -> dict:
    with open(path, 'r') as f:
        return json.loads(f.read())


def load_query_response(path: str) -> QueryResponse:
    try:
        data = load_json(path)
        try:
            return QueryResponse(**data)
        except AttributeError as err:
            LOG.error(f"Invalid data format: {err}")
            exit(-1)
    except OSError as err:
        LOG.error(f"Could not load file {path}: {err}")
        exit(-1)


class EventPublisher:
    def __init__(self, loop):
        self.loop = loop
        self.mqtt_events: List[MqttHistory]
        self.msg_delay: int

    def on_disconnect(self, client, userdata, rc):
        self.disconnected.set_result(rc)

    async def main(self, filename: str, msg_delay: int = 0):
        self.disconnected = self.loop.create_future()
        event_query = load_query_response(filename)
        self.mqtt_events: List[MqttHistory] = [MqttHistory(**e) for e in event_query.results]
        self.msg_delay = msg_delay

        self.client = mqtt.Client(client_id=CLIENT_ID)
        self.client.username_pw_set(os.getenv("MQTT_USER", 'test-user'), os.getenv('MQTT_PASSWORD'))
        self.client.on_disconnect = self.on_disconnect

        aioh = AsyncioHelper(self.loop, self.client)

        self.client.connect(os.getenv('MQTT_HOST', 'localhost'), 1883, 60)
        self.client.socket().setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2048)

        for evt in self.mqtt_events:
            await asyncio.sleep(self.msg_delay)
            LOG.debug("Publishing")
            self.client.publish(evt.topic, json.dumps(evt.payload), qos=1)

        self.client.disconnect()
        LOG.debug("Disconnected: {}".format(await self.disconnected))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Publish MQTT Events to MQTT Broker')
    parser.add_argument('json_data_filename', type=str, help='file name of the json file containing data to publish')
    parser.add_argument('--msg_delay', type=int, default=0, help='The amount of delay between messages (default: 0)')
    args = parser.parse_args()

    LOG.debug("Starting")
    load_dotenv()
    event_loop = asyncio.get_event_loop()
    publisher = EventPublisher(event_loop)
    event_loop.run_until_complete(publisher.main(args.json_data_filename, args.msg_delay))
    event_loop.close()
    LOG.debug("Finished")
