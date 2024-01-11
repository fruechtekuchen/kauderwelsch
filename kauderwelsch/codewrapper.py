import re

WHITESPACE = r"[ \t]+"


class CodeWrapper:
    def __init__(self, file: str):
        self.file = file
        with open(file) as f:
            self.buffer = f.read().strip()
        self.char_index = 0
        self.line_index = 0
        self.buffer_index = 0
        self.buffer_len = len(self.buffer)
        self.last_match = None

    def match(self, pattern, ignore_whitespace: bool = True) -> str:
        if ignore_whitespace:
            self.match(WHITESPACE, False)
        if self.end():
            return ""
        if m := re.match(pattern, self.buffer[self.buffer_index :]):
            self.buffer_index += m.end()
            return m[0]
        return ""

    def consume_newline(self) -> bool:
        if self.end() or self.match(r"\n\s*"):
            self.line_index += 1
            self.char_index = 0
            return True
        return False

    def end(self):
        return self.buffer_index >= self.buffer_len
