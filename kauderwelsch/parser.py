from __future__ import annotations
from .codewrapper import CodeWrapper

# TODO: Load these values from generated tokens file
VARDECL = "noob"
FUNCDECL = "diy"
RETURN = "yeet"

PRINT = "lol"
EXIT = "kys"
SLEEP = "afk"

FUNCCALL = r"\*"

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
        # * print added to globals for testing purpose.
        # ? could also be loaded from config
        self.namespaces = {"global": {"print": "func"}}
        self.namespace = "global"
        self.output = ""
        self.failed = False

    def is_valid_name(self, name: str) -> bool:
        if e := self.get_name_entry(name):
            self.fail(f"{name!r} is already as {e!r} defined")
            return False
        if name in RESERVED:
            self.fail(f"{name!r} is reserved")
            return False
        # ? are there more tests needed
        return True

    def get_name_entry(self, name: str):
        return self.namespaces[self.namespace].get(name, "")

    def set_name_entry(self, name: str, v: str):
        self.namespaces[self.namespace][name] = v

    def parse(self):
        while not self.code.end() and not self.failed:
            if r := self.code.match(KEYWORDS):
                self.parse_keyword(r)
            elif r := self.code.match(SPECIAL):
                self.parse_special(r)
            elif r := self.code.match(IDENTIFIER):
                self.parse_assigment(r)
            elif r := self.code.match(FUNCCALL):
                self.parse_func_call()
                self.parse_newline()
            else:
                self.fail(
                    f"Unable to parse at {self.code.buffer_index} -> \n{self.code.buffer[self.code.buffer_index+20:]}"
                )

    def parse_newline(self):
        if not self.failed and not self.code.newline():
            self.fail("Expected newline")

    def parse_keyword(self, keyword):
        if keyword == "noob":
            self.parse_var_decl()
        elif keyword == "diy":
            self.parse_func_decl()
        else:
            self.fail(f"Unexpected keyword '{keyword}'")
        return 0

    def parse_special(self, special):
        pass

    def parse_var_decl(self):
        variable = self.code.match(IDENTIFIER)
        if not variable:
            self.fail("No variable after noob")
            return
        if not self.is_valid_name(variable):
            return
        self.set_name_entry(variable, "var_")
        if self.code.expect("is"):
            self.parse_assigment(variable)
        else:
            self.parse_newline()

    def parse_assigment(self, variable: str):
        e = self.get_name_entry(variable)
        if e != "var" and e != "var_":
            self.fail("Unkown identifier")
            return
        if not self.code.match("is"):
            self.fail("is Operator missing")
            return
        if e == "var_":
            self.set_name_entry(variable, "var")
        self.output += f"{variable} = "
        self.parse_expression()
        self.output += "\n"
        self.parse_newline()

    def parse_func_decl(self):
        pass

    def parse_func_call(self):
        func = self.code.match(IDENTIFIER)
        if not func:
            self.fail("Function missing")
            return
        if self.get_name_entry(func) != "func":
            self.fail(f"{func!r} is not a function")
            return
        self.output += func + "("
        if self.code.match("with"):
            self.parse_expression()
            while self.code.match(r"\,") and not self.failed:
                self.output += ", "
                self.parse_expression()
        if not self.code.match(FUNCCALL):
            self.fail("Missing closing *")
            return
        self.output += ")"

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
        if v := self.code.match(VALUE):
            self.output += v
        elif v := self.code.match(IDENTIFIER):
            e = self.get_name_entry(v)
            if e == "var_":
                self.fail(f"{v!r} not initialised")
            elif e == "var":
                self.output += v
            else:
                self.fail(f"{v!r} not a variable")
        elif self.code.match(FUNCCALL):
            self.parse_func_call()
        elif self.code.match(r"\("):
            self.output += "("
            self.parse_expression()
            if not self.code.match(r"\)"):
                self.fail("Missing closing bracket")
                return
            self.output += ")"
        else:
            self.fail("Unkown token in expression")

    def write(self, file):
        if not self.failed:
            with open(file, "w") as f:
                f.write(self.output)
        else:
            print("Cant write because parsing failed")

    def fail(self, msg):
        if not self.failed:
            print(f"Error: {msg}")
            self.failed = True
