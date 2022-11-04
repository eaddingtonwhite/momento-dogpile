# momento-dogpile
Demo showing Momento serverless cache w/ dogpile wrapper

### Running

1. Install Dependencies:  `pipenv install`
2. Run:
```
 $ MOMENTO_CACHE=default \
 MOMENTO_AUTH_TOKEN=** \
    pipenv run python example_usage.py

world
foo
[1, 2, 3]
['a', 'b', 'c']
['helloBiz1', 'helloBiz2']

$
```