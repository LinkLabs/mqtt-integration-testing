import asyncio
from logging import getLogger
import paho.mqtt.client as mqtt

LOG = getLogger(__name__)


class AsyncioHelper:
    def __init__(self, loop, client):
        self.loop = loop
        self.client = client
        self.client.on_socket_open = self.on_socket_open
        self.client.on_socket_close = self.on_socket_close
        self.client.on_socket_register_write = self.on_socket_register_write
        self.client.on_socket_unregister_write = self.on_socket_unregister_write

    def on_socket_open(self, client, userdata, sock):
        LOG.debug("Socket opened")

        def cb():
            LOG.debug("Socket is readable, calling loop_read")
            client.loop_read()

        self.loop.add_reader(sock, cb)
        self.misc = self.loop.create_task(self.misc_loop())

    def on_socket_close(self, client, userdata, sock):
        LOG.debug("Socket closed")
        self.loop.remove_reader(sock)
        self.misc.cancel()

    def on_socket_register_write(self, client, userdata, sock):
        LOG.debug("Watching socket for writability.")

        def cb():
            LOG.debug("Socket is writable, calling loop_write")
            client.loop_write()

        self.loop.add_writer(sock, cb)

    def on_socket_unregister_write(self, client, userdata, sock):
        LOG.debug("Stop watching socket for write-ability.")
        self.loop.remove_writer(sock)

    async def misc_loop(self):
        LOG.debug("misc_loop started")
        while self.client.loop_misc() == mqtt.MQTT_ERR_SUCCESS:
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
        LOG.debug("misc_loop finished")
