from __future__ import annotations
from typing import Any, TYPE_CHECKING
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from re import Match
from .tokenizer import Tokenizer
from .tokens import *
from .errors import ParsingError


@dataclass
class Node:
    type: str
    value: Any
    children: list[Node] = field(default_factory=list)

    def add(self, to_add: Node | list[Node]):
        if isinstance(to_add, list):
            self.children.extend(to_add)
        else:
            self.children.append(to_add)

    def __str__(self) -> str:
        return f"{self.type}({self.value})"


class Parser:
    def __init__(self, file: str) -> None:
        self.file = file
        self.tokenizer = Tokenizer(file)
        #! Globals should be loaded not static
        self.scopes = {"global": {"test": ("int", "int")}, "root": {}}
        self.globals = self.scopes["global"]
        self.current_scope = self.scopes["root"]
        self.ast = Node("ROOT", file, [])

    def check_valid(self, name: str):
        if name in self.current_scope:
            raise ParsingError("Name already in use")
        if name in RESERVED:
            raise ParsingError("Invalid name")

    def check_type(self, name: str, type: Any):
        if (o := self.current_scope.get(name, None)) is not None:
            if not isinstance(o, type):
                raise ParsingError("Wrong type")
            return o
        elif (o := self.globals.get(name, None)) is not None:
            if not isinstance(o, type):
                raise ParsingError("Wrong type")
            return o
        raise ParsingError("Unknown name")

    def parse(self):
        while not self.tokenizer.end():
            if m := self.tokenizer.match(VARDECL):
                parsed = self.parse_var_decl(m[1])
            elif m := self.tokenizer.match(FUNCDECL):
                parsed = self.parse_func_decl()
            elif m := self.tokenizer.match(IDENTIFIER):
                parsed = self.parse_assignment(m[0])
            else:
                raise ParsingError("Unknown token")
            self.ast.add(parsed)
            self.tokenizer.consume_newline()

    def parse_func_decl(self):
        pass

    def parse_var_decl(self, name):
        self.check_valid(name)
        if m := self.tokenizer.match("is"):
            expr = self.parse_expression()
            var_type = self.expression_to_type(expr)
            self.current_scope[name] = var_type
            return Node("VARINIT", name, expr)
        else:
            self.current_scope[name] = ""
            return Node("VARDECL", name)

    def parse_expression(self):
        expr = []
        expr.append(self.parse_primary())
        while op := self.tokenizer.match(OPERATORS):
            expr.append(Node("OPERATOR", op[0]))
            expr.append(self.parse_primary())
        return expr

    def parse_primary(self):
        if m := self.tokenizer.match(VALUE):
            return Node("LITERAL", m[0])
        elif self.tokenizer.match(r"\("):
            inner = self.parse_expression()
            self.tokenizer.expect(r"\)")
            return Node("PARAN", "", inner)
        elif self.tokenizer.match(r"\*"):
            return self.parse_func_call()
        elif m := self.tokenizer.match(IDENTIFIER):
            self.check_type(m[0], str)
            return Node("VAR", m[0])
        else:
            raise ParsingError("Expected primary")

    def expression_to_type(self, expr: Node):
        # TODO: Actually determining the correct type
        return "int"

    def parse_func_call(self):
        func = self.tokenizer.expect(IDENTIFIER)[0]
        params = self.check_type(func, tuple)
        if not params:
            self.tokenizer.expect(r"\*")
            return Node("CALL", func)
        self.tokenizer.expect("with")
        args = []
        count = 0
        while True:
            expr = self.parse_expression()
            args.append(Node("ARG", "", expr))
            count += 1
            if count > len(params):
                raise ParsingError("Too many arguments")
            if self.tokenizer.match(r","):
                continue
            elif count < len(params):
                raise ParsingError("Too few arguments")
            break
        self.tokenizer.expect(r"\*")
        return Node("CALL", func, args)

    def parse_assignment(self, name):
        self.check_type(name, str)
        self.tokenizer.expect("is")
        expr = self.parse_expression()
        if not self.current_scope[name]:
            var_type = self.expression_to_type(expr)
            self.current_scope[name] = var_type
        return Node("ASSIGN", name, expr)

    def print_ast(self, node=None, level=0):
        if not node:
            node = self.ast
        print(" " * level + f"{'>' if node.children else '-'} {node}")
        for child in node.children:
            if child:
                self.print_ast(child, level + 2)
