import asyncio
import os
import subprocess
import sysconfig

import pytest
from asphalt.core.context import Context

from asphalt.wamp.client import WAMPClient


@pytest.fixture
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope='session')
def virtualenv(tmpdir_factory):
    venv_dir = tmpdir_factory.mktemp('virtualenv')
    subprocess.check_call(['virtualenv', str(venv_dir)])
    yield venv_dir
    venv_dir.remove()


@pytest.fixture(scope='session')
def crossbar(virtualenv):
    # Crossbar has pinned dependencies and thus cannot be safely installed in the same testing
    # environment as asphalt-wamp itself. So, we install it in a temporary virtualenv instead.
    scripts_dirname = os.path.basename(sysconfig.get_path('scripts'))
    scripts_dir = virtualenv.join(scripts_dirname)
    subprocess.check_call([str(scripts_dir.join('pip')), 'install', 'crossbar ~= 16.10.1'])

    # Launch Crossbar
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    args = [str(scripts_dir.join('crossbar')), 'start', '--config', config_path]
    env = {'PYTHONUNBUFFERED': '1'}
    process = subprocess.Popen(args, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Read output until a line is found that confirms the first transport is ready
    for line in process.stdout:
        if b"transport 'transport-001' started" in line:
            break
    else:
        raise RuntimeError('crossbar failed to start: ' + process.stderr.read().decode())

    yield process

    process.terminate()


@pytest.fixture
def wampclient(request, event_loop, crossbar):
    kwargs = getattr(request, 'param', {})
    client = WAMPClient(port=8090, **kwargs)
    event_loop.run_until_complete(client.start(Context()))
    yield client
    event_loop.run_until_complete(client.disconnect())
