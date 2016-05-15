from pubnub import utils
from pubnub.endpoints.endpoint import Endpoint
from pubnub.errors import PNERR_MESSAGE_MISSING, PNERR_CHANNEL_MISSING, \
    PNERR_PUBLISH_META_WRONG_TYPE
from pubnub.exceptions import PubNubException
from pubnub.models.consumer.pubsub import PNPublishResult
from pubnub.enums import HttpMethod


class Publish(Endpoint):
    # /publish/<pub_key>/<sub_key>/<signature>/<channel>/<callback>/<message>[?argument(s)]
    PUBLISH_PATH = "/publish/%s/%s/0/%s/%s/%s"

    def __init__(self, pubnub):
        Endpoint.__init__(self, pubnub)
        self._channel = None
        self._message = None
        self._should_store = None
        self._use_post = None
        self._meta = None

    def channel(self, channel):
        self._channel = str(channel)
        return self

    def message(self, message):
        self._message = message
        return self

    def use_post(self, use_post):
        self._use_post = bool(use_post)
        return self

    def should_store(self, should_store):
        self._should_store = bool(should_store)
        return self

    def meta(self, meta):
        self._meta = meta
        return self

    def build_params(self):
        params = self.default_params()

        if self._meta is not None:
            if not isinstance(self._meta, dict):
                raise PubNubException(pn_error=PNERR_PUBLISH_META_WRONG_TYPE)
            params['meta'] = utils.url_encode(utils.write_value_as_string(self._meta))

        if self._should_store is not None:
            if self._should_store:
                params["store"] = "1"
            else:
                params["store"] = "0"

        return params

    def build_path(self):
        # TODO: encrypt if cipher key is set
        stringified_message = utils.url_encode(utils.write_value_as_string(self._message))

        # TODO: add option to publish with POST
        return Publish.PUBLISH_PATH % (self.pubnub.config.publish_key, self.pubnub.config.subscribe_key,
                                       self._channel, 0, stringified_message)

    def http_method(self):
        return HttpMethod.GET

    def validate_params(self):
        if self._channel is None or len(self._channel) is 0:
            raise PubNubException(pn_error=PNERR_CHANNEL_MISSING)

        if self._message is None:
            raise PubNubException(pn_error=PNERR_MESSAGE_MISSING)

        self.validate_subscribe_key()
        self.validate_publish_key()

        pass

    def create_response(self, envelope):
        """
        :param envelope: an already serialized json response
        :return:
        """

        timetoken = int(envelope[2])

        res = PNPublishResult(timetoken)

        return res