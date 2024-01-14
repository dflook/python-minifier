class RemoveUnusedPlatformOptions(object):
    """
    Options for the RemoveUnusedPlatform transform

    This can be passed to the minify function as the remove_unused_platforms argument

    :param platform_test_key: The key used to indicate a platform check statement
    :type platform_test_key: str
    :param platform_preserve_value: The value of the test to keep
    :type platform_preserve_value: str
    """

    platform_test_key = "_PLATFORM"
    platform_preserve_value = "linux"

    def __init__(self, platform_test_key="", platform_preserve_value=""):
        self.platform_test_key = platform_test_key
        self.platform_preserve_value = platform_preserve_value

    def __repr__(self):
        return 'RemoveUnusedPlatformOptions(platform_test_key=%s, platform_preserve_value=%s)' % (self.platform_test_key, self.platform_preserve_value)

    def __nonzero__(self):
        return any((self.platform_test_key, self.platform_preserve_value))

    def __bool__(self):
        return self.__nonzero__()
