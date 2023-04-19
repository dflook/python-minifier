import pytest
def skip_invalid(test):
    def wrapper(statement):
        if isinstance(statement, tuple):
            statement, valid_condition = statement
            if valid_condition is False:
                pytest.skip('not supported in this version of Python')
        test(statement)
    return wrapper
