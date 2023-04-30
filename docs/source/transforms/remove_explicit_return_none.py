def important(a):
    if a > 3:
        return a
    if a < 2:
        return None
    a.adjust(1)
    return None
