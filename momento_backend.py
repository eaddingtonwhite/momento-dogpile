import logging

from momento import CacheClient, Configurations, CredentialProvider
from momento.responses import CacheGet, CacheSet, CreateCache, ListCaches 
from dogpile.cache.api import BytesBackend, DefaultSerialization

_logger = logging.getLogger("MomentoBackend")


class MomentoBackend(BytesBackend):
    r"""
    A `Momento Cache <https://gomomento.com/>`_ backend

    Example configuration::
        from dogpile.cache import make_region
        region = make_region().configure(
            'dogpile.cache.momento',
            arguments = {
                'apiKey': 'os.getenv("MOMENTO_API_KEY")',
                'cacheName': 'my-cache',
                'ttl': 3600,
            }
        )

        Arguments accepted in the arguments dictionary:

        :param apiKey: string. Your Momento Api Key
        :param cacheNamet: string. Then name of the cache to use on Momento``.
        :param defaultTTL: integer. the default ttl to use when setting items in Momento Backend .
    """
    def __init__(self, arguments):
        arguments = arguments.copy()
        self.apiKey = arguments.pop("apiKey")
        self.cacheName = arguments.pop("cacheName")
        self.ttl = arguments.pop("ttl")

        # Forces all keys to string behind scenes
        self.key_mangler = str

        # Init momento cache client
        self.client = CacheClient.create(Configurations.Laptop.v1(), CredentialProvider.from_string(self.apiKey), self.ttl)

        # try to create cache if doesn't already exist
        create_cache_response = self.client.create_cache(self.cacheName)
        match create_cache_response:
            case CreateCache.Success():
                pass
            case CreateCache.CacheAlreadyExists():
                _logger.info(f"Cache with name: {self.cacheName!r} already exists.")
            case CreateCache.Error() as error:
                _logger.error(f"Error creating cache: {error.message}")
            case _:
                _logger.error("Unreachable")

    def get_serialized(self, key):
        return self.client.get(self.cacheName, key).value_bytes

    def get_serialized_multi(self, keys):
        multi_get_responses = []
        for key in keys:
            multi_get_responses.append(self.client.get(self.cacheName, key).value_bytes)
        return multi_get_responses

    def set_serialized(self, key, value):
        self.client.set(self.cacheName, key, value)

    def set_serialized_multi(self, mapping):
        for key in mapping:
            self.client.set(self.cacheName, key, mapping[key])

    def delete(self, key):
        self.client.delete(self.cacheName, key)

    def delete_multi(self, keys):
        for key in keys:
            # FIXMe come back and add true multi delete once added in momento sdk vs looping like this
            self.client.delete(self.cacheName, key)
