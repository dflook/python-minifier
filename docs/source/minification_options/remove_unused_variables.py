TIMEOUT = 30
RETRIES = TIMEOUT * 2
VERSION = '1.0'
__version__ = VERSION

started = start()


def process(items):
    total = 0
    scratch = [item for item in items]
    lookup = {'a': 1}
    for item in items:
        total += item
    return total


print(RETRIES)
