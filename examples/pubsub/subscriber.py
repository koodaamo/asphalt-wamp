"""
This example demonstrates how to subscribe to topics with WAMP.

First start subscriber.py and take note of which port it's running on.
You will need to give this port number as the first argument to this script.
"""

import logging
import sys

from asphalt.core import ContainerComponent, Context, run_application
from asphalt.wamp.context import EventContext

logger = logging.getLogger(__name__)


def subscriber(ctx: EventContext, message: str):
    logger.info('Received message from %s: %s', ctx.topic, message)


class PublisherComponent(ContainerComponent):
    async def start(self, ctx: Context):
        self.add_component('wamp', url='ws://localhost:8080')
        await super().start(ctx)

        topic = sys.argv[1]
        await ctx.wamp.subscribe(subscriber, topic)
        logger.info('Subscribed to topic: %s', topic)

if len(sys.argv) < 2:
    print('Usage: {} <topic>'.format(sys.argv[0]), file=sys.stderr)
    sys.exit(1)

run_application(PublisherComponent(), logging=logging.INFO)
