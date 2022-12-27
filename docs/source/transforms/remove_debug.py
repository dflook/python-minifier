value = 10

# Truthy
if __debug__:
    value += 1

if __debug__ is True:
    value += 1

if __debug__ is not False:
    value += 1

if __debug__ == True:
    value += 1


# Falsy
if not __debug__:
    value += 1

if __debug__ is False:
    value += 1

if __debug__ is not True:
    value += 1

if __debug__ == False:
    value += 1

print(value)