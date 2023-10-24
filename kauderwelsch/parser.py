from __future__ import annotations
from .codewrapper import CodeWrapper

# TODO: Load these values from generated tokens file
VARDECL = "noob"
FUNCDECL = "diy"
RETURN = "yeet"

PRINT = "lol"
EXIT = "kys"
SLEEP = "afk"

KEYWORDS = f"\\b({VARDECL}|{RETURN}|{FUNCDECL})"
WHITESPACE = r"\s+"
SPECIAL = f"(i?)\b({PRINT}|{EXIT}|{SLEEP})\b"
IDENTIFIER = r"\b\w+\b"
VALUE = r"\b[+-]?\d+\b"
OPERATORS = r"w/o|w/|x|/"

OP_TRANS = {"w/": "+", "w/o": "-", "x": "*", "/": "/"}

RESERVED = [VARDECL, FUNCDECL, RETURN, PRINT, EXIT, SLEEP, "is", "with"]


class RDParser:
    def __init__(self, file: str):
        self.code = CodeWrapper(file)
        self.namespaces = {"global": {}}
        self.namespace = "global"
        self.output = ""
        self.failed = False

    def is_valid_name(self, name: str) -> bool:
        if name in self.namespaces[self.namespace]:
            return False
        if name in RESERVED:
            return False
        # ? More tests needed?
        return True

    def get_name_entry(self, name: str):
        return self.namespaces[self.namespace].get(name, "")

    def parse(self):
        while not self.code.end() and not self.failed:
            if r := self.code.match(KEYWORDS):
                self.parse_keyword(r)
            elif r := self.code.match(SPECIAL):
                self.parse_special(r)
            elif r := self.code.match(IDENTIFIER):
                self.parse_assigment(r)
            else:
                print(
                    f"Unable to parse at {self.code.buffer_index} -> \n{self.code.buffer[self.code.buffer_index+20:]}"
                )
                self.failed = True

    def parse_newline(self):
        if not self.code.newline():
            print("Expected newline")
            self.failed = True

    def parse_keyword(self, keyword):
        if keyword == "noob":
            self.parse_var_decl()
        elif keyword == "diy":
            self.parse_func_decl()
        else:
            print(f"Unexpected keyword '{keyword}'")
            self.failed = True
        return 0

    def parse_special(self, special):
        pass

    def parse_var_decl(self):
        variable = self.code.match(IDENTIFIER)
        if not variable:
            print("No variable after noob")
            self.failed = True
            return
        if not self.is_valid_name(variable):
            print("Invalid variable name")
            self.failed = True
            return
        self.namespaces["global"][variable] = "var"
        if self.code.expect("is"):
            self.parse_assigment(variable)
        else:
            self.parse_newline()

    def parse_assigment(self, variable: str):
        if self.get_name_entry(variable) != "var":
            print("Unkown identifier")
            self.failed = True
            return
        if not self.code.match("is"):
            print("is Operator missing")
            self.failed = True
            return
        self.output += f"{variable} = "
        self.parse_expression()
        self.output += "\n"
        self.parse_newline()

    def parse_func_decl(self):
        pass

    def parse_expression(self):
        self.parse_primary()
        while self.parse_operator() and not self.failed:
            self.parse_primary()

    def parse_operator(self):
        o = self.code.expect(OPERATORS)
        if not o:
            return False
        self.code.consume()
        self.output += " " + OP_TRANS[o] + " "
        return True

    def parse_primary(self):
        # TODO: variables, function calls and brackets
        v = self.code.match(VALUE)
        if not v:
            print("Expected Value")
            self.failed = True
            return ""
        self.output += v

    def write(self, file):
        if not self.failed:
            with open(file, "w") as f:
                f.write(self.output)
        else:
            print("Cant write because parsing failed")
