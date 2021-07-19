BACKSLASH = '\\'

def Str(string):

    candidates = []

    for quote in ['"', "'",  '"""', "'''",]:
        c = quote + str(MiniString(string, quote)) + quote
        candidates.append(c)

    for quote in ['"', "'",  '"""', "'''",]:
        try:
            c = 'r' + quote + str(MiniRawString(string, quote)) + quote
            candidates.append(c)
        except:
            pass

    if not candidates:
        return repr(string)

    return min(candidates, key=len)

class MiniString(object):
    """
    Create a representation of a string object

    :param str string: The string to minify

    """

    def __init__(self, string, quote="'"):
        self._s = string
        self.safe_mode = False
        self.quote = quote

    def __str__(self):
        """
        The smallest python literal representation of a string

        :rtype: str

        """

        if self._s == '':
            return ''

        if len(self.quote) == 1:
            s = self.to_short()
        else:
            s = self.to_long()

        try:
            eval(self.quote + s + self.quote)
        except (UnicodeDecodeError, UnicodeEncodeError):
            if self.safe_mode:
                raise

            self.safe_mode = True

        assert eval(self.quote + s + self.quote) == self._s

        return s

    def to_short(self):
        s = ''

        escaped = {
            '\n': BACKSLASH + 'n',
            '\\': BACKSLASH + BACKSLASH,
            '\a': BACKSLASH + 'a',
            '\b': BACKSLASH + 'b',
            '\f': BACKSLASH + 'f',
            '\r': BACKSLASH + 'r',
            '\t': BACKSLASH + 't',
            '\v': BACKSLASH + 'v',
            '\0': BACKSLASH + 'x00',
            self.quote: BACKSLASH + self.quote,
        }

        for c in self._s:
            if c in escaped.keys():
                s += escaped[c]
            else:
                if self.safe_mode:
                    unicode_value = ord(c)
                    if unicode_value <= 0x7F:
                        s += c
                    elif unicode_value <= 0xFFFF:
                        s += BACKSLASH + 'u' + format(unicode_value, '04x')
                    else:
                        s += BACKSLASH + 'U' + format(unicode_value, '08x')
                else:
                    s += c

        return s

    def to_long(self):
        s = ''

        escaped = {
            '\\': BACKSLASH + BACKSLASH,
            '\a': BACKSLASH + 'a',
            '\b': BACKSLASH + 'b',
            '\f': BACKSLASH + 'f',
            '\r': BACKSLASH + 'r',
            '\t': BACKSLASH + 't',
            '\v': BACKSLASH + 'v',
            '\0': BACKSLASH + 'x00',
            self.quote[0]: BACKSLASH + self.quote[0],
        }

        for c in self._s:
            if c in escaped.keys():
                s += escaped[c]
            else:
                if self.safe_mode:
                    unicode_value = ord(c)
                    if unicode_value <= 0x7F:
                        s += c
                    elif unicode_value <= 0xFFFF:
                        s += BACKSLASH + 'u' + format(unicode_value, '04x')
                    else:
                        s += BACKSLASH + 'U' + format(unicode_value, '08x')
                else:
                    s += c

        return s

class MiniRawString(object):
    """
    Create a representation of a string object

    :param str string: The string to minify

    """

    def __init__(self, string, quote="'"):
        self._s = string
        self.quote = quote

    def __str__(self):
        if self._s == '':
            return ''

        assert eval('r' + self.quote + self._s + self.quote) == self._s

        return self._s

def Bytes(b):

    candidates = []

    for quote in ['"', "'",  '"""', "'''"]:
        try:
            c = 'b' + quote + str(MiniBytes(b, quote)) + quote
            candidates.append(c)
        except:
            pass

    for quote in ['"', "'",  '"""', "'''"]:
        try:
            c = 'rb' + quote + str(MiniRawBytes(b, quote)) + quote
            candidates.append(c)
        except Exception as e:
            pass

    if not candidates:
        return repr(b)

    return min(candidates, key=len)

class MiniBytes(object):
    """
    Create a representation of a bytes object

    :param bytes string: The string to minify

    """

    def __init__(self, bytes_, quote="'"):
        self._b = bytes_
        self.quote = quote

    def __str__(self):

        if self._b == b'':
            return ''

        if len(self.quote) == 1:
            s = self.to_short()
        else:
            s = self.to_long()

        assert eval('b' + self.quote + s + self.quote) == self._b

        return s

    def to_short(self):
        b = ''

        for c in self._b:
            if c == b'\x00'[0]:
                b += BACKSLASH + 'x00'
            elif c == b'\\'[0]:
                b += BACKSLASH + BACKSLASH
            elif c == b'\n'[0]:
                b += BACKSLASH + 'n'
            elif c == b'\r'[0]:
                b += BACKSLASH + 'r'
            elif c == ord(self.quote[0]):
                b += BACKSLASH + self.quote
            else:
                if c >= 128:
                    b += BACKSLASH + 'x' + hex(c)[2:]
                else:
                    b += chr(c)

        return b

    def to_long(self):
        b = ''

        for c in self._b:
            if c == b'\x00'[0]:
                b += BACKSLASH + 'x00'
            elif c == b'\r'[0]:
                b += BACKSLASH + 'r'
            elif c == b'\\'[0]:
                b += BACKSLASH + BACKSLASH
            elif c == ord(self.quote[0]):
                b += BACKSLASH + self.quote[0]
            else:
                if c >= 128:
                    b += BACKSLASH + 'x' + hex(c)[2:]
                else:
                    b += chr(c)

        return b

class MiniRawBytes(object):

    def __init__(self, b, quote="'"):
        self._b = b
        self.quote = quote

    def __str__(self):

        if self._b == b'':
            return ''

        if len(self.quote) == 1:
            s = self.to_short()
        else:
            s = self.to_long()

        assert eval('rb' + self.quote + s + self.quote) == self._b

        return s

    def to_short(self):
        b = ''

        for c in self._b:
          b += chr(c)

        return b

    def to_long(self):
        b = ''

        for c in self._b:
          b += chr(c)

        return b
