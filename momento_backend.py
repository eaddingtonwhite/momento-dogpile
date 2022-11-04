import logging

import momento.errors as errors
import momento.simple_cache_client as scc
from dogpile.cache.api import BytesBackend, DefaultSerialization

_logger = logging.getLogger("MomentoBackend")


class MomentoBackend(BytesBackend):
    r"""
    A `Momento Serverless Cache <https://gomomento.com/>`_ backend

    Example configuration::
        from dogpile.cache import make_region
        region = make_region().configure(
            'dogpile.cache.momento',
            arguments = {
                'authToken': 'os.getenv("MOMENTO_AUTH_TOKEN")',
                'cacheName': 'my-cache',
                'ttl': 3600,
            }
        )

        Arguments accepted in the arguments dictionary:

        :param authToken: string. Your Momento AuthToken
        :param cacheNamet: string. Then name of the cache to use on Momento``.
        :param defaultTTL: integer. the default ttl to use when setting items in Momento Backend .
    """
    def __init__(self, arguments):
        arguments = arguments.copy()
        self.authToken = arguments.pop("authToken")
        self.cacheName = arguments.pop("cacheName")
        self.ttl = arguments.pop("ttl")

        # Forces all keys to string behind scenes
        self.key_mangler = str

        # Init momento cache client
        self.client = scc.SimpleCacheClient(self.authToken, self.ttl)

        # try to create cache if doesnt already exist
        try:
            self.client.create_cache(self.cacheName)
        except errors.AlreadyExistsError:
            _logger.info(f"Cache with name: {self.cacheName!r} already exists.")

    def get_serialized(self, key):
        return self.client.get(self.cacheName, key).value_as_bytes()

    def get_serialized_multi(self, keys):
        return self.client.get_multi(self.cacheName, *keys).values_as_bytes()

    def set_serialized(self, key, value):
        self.client.set(self.cacheName, key, value)

    def set_serialized_multi(self, mapping):
        self.client.set_multi(
            cache_name=self.cacheName,
            items={k: v for k, v in mapping.items()}
        )

    def delete(self, key):
        self.client.delete(self.cacheName, key)

    def delete_multi(self, keys):
        for key in keys:
            # FIXMe come back and add true multi delete once added in momento sdk vs looping like this
            self.client.delete(self.cacheName, key)
