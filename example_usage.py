import os

from dogpile.cache import make_region
from dogpile.cache import register_backend

# manually register our custom backend cache driver for demo since not in main repo yet
register_backend("momento", "momento_backend", "MomentoBackend")

# set up and configure dogpile cache
region = make_region("myregion")
region.configure(
    "momento",
    arguments={
        'authToken': os.getenv("MOMENTO_AUTH_TOKEN"),
        'cacheName': os.getenv("MOMENTO_CACHE"),
        'ttl': 3600,
    })

# Test basic string key
data = region.set("hello", "world")
print(region.get("hello"))

# test int key
data = region.set(2, "foo")
print(region.get(2))

# test multi with string keys
region.set_multi({"a": 1, "b": 2, "c": 3})
print(region.get_multi(["a", "b", "c"]))

# test multi with int keys
region.set_multi({1: "a", 2: "b", 3: "c"})
print(region.get_multi([1, 2, 3]))


class Biz:
    a = 0


# Test with complex object keys
biz1 = Biz()
biz2 = Biz()
region.set(biz1, "helloBiz1")
region.set(biz2, "helloBiz2")
print(region.get_multi([biz1, biz2]))
