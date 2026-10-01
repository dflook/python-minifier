def check(value):
    if value < 0:
        raise ValueError(value)
        print('never runs')

    if value:
        return 'set'
    else:
        return 'unset'

    print('never runs')


def first(items):
    for item in items:
        if item:
            return item
    print('runs if there are no items')
    return None


def generator():
    return
    yield
