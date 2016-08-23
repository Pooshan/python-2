import asyncio
import pytest

from pubnub.pubnub_asyncio import PubNubAsyncio, SubscribeListener
from tests.helper import pnconf_sub_copy
from tests.integrational.vcr_asyncio_sleeper import get_sleeper
from tests.integrational.vcr_helper import pn_vcr


@get_sleeper('tests/integrational/fixtures/asyncio/here_now/single_channel.yaml')
@pn_vcr.use_cassette('tests/integrational/fixtures/asyncio/here_now/single_channel.yaml')
@pytest.mark.asyncio
def test_single_channel(event_loop, sleeper=asyncio.sleep):
    pubnub = PubNubAsyncio(pnconf_sub_copy(), custom_event_loop=event_loop)
    pubnub.config.uuid = 'test-here-now-asyncio-uuid1'
    ch = "test-here-now-asyncio-ch"

    callback = SubscribeListener()
    pubnub.add_listener(callback)
    pubnub.subscribe().channels(ch).execute()

    yield from callback.wait_for_connect()

    yield from sleeper(5)

    env = yield from pubnub.here_now() \
        .channels(ch) \
        .include_uuids(True) \
        .future()

    assert env.result.total_channels == 1
    assert env.result.total_occupancy >= 1

    channels = env.result.channels

    assert len(channels) == 1
    assert channels[0].occupancy == 1
    assert channels[0].occupants[0].uuid == pubnub.uuid

    pubnub.unsubscribe().channels(ch).execute()
    yield from callback.wait_for_disconnect()

    pubnub.stop()


@get_sleeper('tests/integrational/fixtures/asyncio/here_now/multiple_channels.yaml')
@pn_vcr.use_cassette('tests/integrational/fixtures/asyncio/here_now/multiple_channels.yaml',
                     match_on=['method', 'scheme', 'host', 'port', 'string_list_in_path', 'query'],
                     match_on_kwargs={
                         'string_list_in_path': {
                             'positions': [4, 6]
                         }
                     })
@pytest.mark.asyncio
def test_multiple_channels(event_loop, sleeper=asyncio.sleep):
    pubnub = PubNubAsyncio(pnconf_sub_copy(), custom_event_loop=event_loop)
    pubnub.config.uuid = 'test-here-now-asyncio-uuid1'

    ch1 = "test-here-now-asyncio-ch1"
    ch2 = "test-here-now-asyncio-ch2"

    callback = SubscribeListener()
    pubnub.add_listener(callback)
    pubnub.subscribe().channels([ch1, ch2]).execute()

    yield from callback.wait_for_connect()

    yield from sleeper(5)
    env = yield from pubnub.here_now() \
        .channels([ch1, ch2]) \
        .future()

    assert env.result.total_channels == 2
    assert env.result.total_occupancy >= 1

    channels = env.result.channels

    assert len(channels) == 2
    assert channels[0].occupancy == 1
    assert channels[0].occupants[0].uuid == pubnub.uuid
    assert channels[1].occupancy == 1
    assert channels[1].occupants[0].uuid == pubnub.uuid

    pubnub.unsubscribe().channels([ch1, ch2]).execute()
    yield from callback.wait_for_disconnect()

    pubnub.stop()


@get_sleeper('tests/integrational/fixtures/asyncio/here_now/global.yaml')
@pn_vcr.use_cassette('tests/integrational/fixtures/asyncio/here_now/global.yaml',
                     match_on=['method', 'scheme', 'host', 'port', 'string_list_in_path', 'query'],
                     match_on_kwargs={
                         'string_list_in_path': {
                             'positions': [4]
                         }
                     })
@pytest.mark.asyncio
def test_global(event_loop, sleeper=asyncio.sleep):
    pubnub = PubNubAsyncio(pnconf_sub_copy(), custom_event_loop=event_loop)
    pubnub.config.uuid = 'test-here-now-asyncio-uuid1'

    ch1 = "test-here-now-asyncio-ch1"
    ch2 = "test-here-now-asyncio-ch2"

    callback = SubscribeListener()
    pubnub.add_listener(callback)
    pubnub.subscribe().channels([ch1, ch2]).execute()

    yield from callback.wait_for_connect()

    yield from sleeper(5)

    env = yield from pubnub.here_now().future()

    assert env.result.total_channels >= 2
    assert env.result.total_occupancy >= 1

    pubnub.unsubscribe().channels([ch1, ch2]).execute()
    yield from callback.wait_for_disconnect()

    pubnub.stop()
