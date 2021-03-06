"""
This example demonstrates the use of a WAMP registry to register a procedure handler and an event
subscriber.
"""

from pathlib import Path
import logging

from asphalt.core import ContainerComponent, Context, run_application
from asphalt.wamp.context import CallContext, EventContext
from asphalt.wamp.registry import WAMPRegistry
from asphalt.wamp.utils import launch_crossbar

registry = WAMPRegistry()
subregistry = WAMPRegistry('test')
registry.add_from(subregistry)


@subregistry.procedure
async def reverse(ctx: CallContext, message: str):
    return message[::-1]


@subregistry.subscriber('topic.subtopic')
async def subtopic(ctx: EventContext, message):
    print('message received from topic.subtopic: %s' % message)


class RPCServerComponent(ContainerComponent):
    async def start(self, ctx: Context):
        crossbar_dir = Path(__name__).parent / '.crossbar'
        launch_crossbar(crossbar_dir)

        self.add_component('wamp', url='ws://localhost:8080', registry=registry)
        await super().start(ctx)

run_application(RPCServerComponent(), logging=logging.INFO)
