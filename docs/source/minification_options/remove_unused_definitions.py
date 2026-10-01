def helper():
    return 1


def unused():
    return helper()


class Unused:
    def method(self):
        return 1


@register
def registered():
    pass


def main():
    def inner():
        pass
    return 2


print(main())
