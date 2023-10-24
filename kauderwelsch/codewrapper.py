import re

WHITESPACE = r"[ \t]+"


class CodeWrapper:
    def __init__(self, file: str):
        self.file = file
        with open(file) as f:
            self.buffer = f.read()
        self.char_index = 0
        self.line_index = 0
        self.buffer_index = 0
        self.buffer_len = len(self.buffer)
        self.last_match = None

    def expect(self, pattern: str, ignore_whitespace: bool = True) -> str:
        return self.match(pattern, ignore_whitespace, False)

    def match(
        self, pattern, ignore_whitespace: bool = True, consume: bool = True
    ) -> str:
        if ignore_whitespace:
            self.match(WHITESPACE, False)
        if self.end():
            return ""
        if m := re.match(pattern, self.buffer[self.buffer_index :]):
            if consume:
                self.buffer_index += m.end()
                self.last_match = None
            else:
                self.last_match = m
            return m[0]
        return ""

    def consume(self):
        self.buffer_index += self.last_match.end()
        self.last_match = None

    def newline(self) -> bool:
        if self.end() or self.match("\n"):
            self.line_index += 1
            self.char_index = 0
            return True
        return False

    def end(self):
        return self.buffer_index >= self.buffer_len
