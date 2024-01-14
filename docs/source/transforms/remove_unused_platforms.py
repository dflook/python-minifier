value = 10
_PLATFORM = "linux"  # Normally this is derived from sys.uname or platform.

# Supported Statements that will be kept in this example
if _PLATFORM == "linux":
    value += 1


# Supported Statements that will be removed in this example
if _PLATFORM == "armchair":
    value += 1

# Basic if/elif can be used

if _PLATFORM == "linux":
    value += 1
elif _PLATFORM == "armchair":
    value += 1

# So can else
if _PLATFORM == "armchair":
    value += 1
else:
    value += 1

# Statements that are not supported by PyMinify
if _PLATFORM:
    value += 1

if _PLATFORM in ["linux", "windows"]:
    value += 1


print(value)
