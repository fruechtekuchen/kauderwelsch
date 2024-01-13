from __future__ import annotations
from typing import Any, TYPE_CHECKING
from dataclasses import dataclass, field

if TYPE_CHECKING:
    from re import Match
from .tokenizer import Tokenizer
from .constants import *
from .errors import ParsingError


@dataclass
class Scope:
    parent: None | Scope = None
    scope: dict[str, dict] = field(
        default_factory=lambda: {"func": {}, "var": {}, "type": {}}
    )

    def get_classes(self, name: str) -> set[str]:
        classes = set()
        for class_, names in self.scope.items():
            if name in names:
                classes.add(class_)
        return classes

    def check_class(self, name: str, class_: str) -> bool:
        return class_ in self.get_classes(name)

    def get(self, class_: str, name: str) -> Any | None:
        return self.scope[class_].get(name, None)

    def set(self, class_: str, name: str, value: Any):
        self.scope[class_][name] = value

    def check_value(self, class_: str, name: str, value: Any) -> bool:
        return self.get(class_, name) == value

    def check_name(self, class_: str, name: str) -> bool:
        return name in self.scope[class_]


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


class NameSpace:
    def __init__(self):
        self.scopes = {S_ROOT: Scope(), S_GLOBAL: Scope()}
        self.current_scope = self.scopes[S_ROOT]
        self.globals = self.scopes[S_GLOBAL]
        #! defaults should be loaded not set statically
        self.globals.set("type", "int", "")

    def exit_scope(self):
        assert self.current_scope.parent
        self.current_scope = self.current_scope.parent

    def new_scope(self, name: str):
        assert name not in self.scopes
        self.scopes[name] = Scope(self.current_scope)
        self.current_scope = self.scopes[name]

    def switch_scope(self, name: str):
        assert name in self.scopes
        self.current_scope = self.scopes[name]

    def check_name(self, class_: str, name: str):
        if self.current_scope.check_name(class_, name) or name in RESERVED:
            raise ParsingError("Invalid name")

    def set(self, class_: str, name: str, value: Any):
        self.current_scope.set(class_, name, value)

    def get(self, class_: str, name: str):
        curr = self.current_scope
        while curr:
            if (o := curr.get(class_, name)) is not None:
                return o
            curr = curr.parent
        if (o := self.globals.get(class_, name)) is not None:
            return o
        raise ParsingError("Unknown name")

    def check_value(self, class_: str, name: str, value: Any):
        if self.get(class_, name) != value:
            raise ParsingError(f"Invalid type, expected {type!r}")

    def get_classes(self, name: str):
        curr = self.current_scope
        classes = set()
        while curr:
            classes = classes.union(curr.get_classes(name))
            curr = curr.parent
        classes = classes.union(self.globals.get_classes(name))
        return classes

    def check_class(self, class_: str, name: str):
        if class_ not in self.get_classes(name):
            raise ParsingError("Invalid class")


class Parser:
    def __init__(self, file: str) -> None:
        self.file = file
        self.tokenizer = Tokenizer(file)
        self.namespace = NameSpace()

        self.ast = Node("ROOT", file, [])

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
        func = self.tokenizer.expect(IDENTIFIER)[0]
        self.namespace.check_name("func", func)
        return_type = ""
        if self.tokenizer.match("as"):
            return_type = self.tokenizer.expect(TYPE)[0]
            self.namespace.check_class("type", return_type)
        signature = []
        params = []
        self.namespace.new_scope(func)
        if self.tokenizer.match("with"):
            while True:
                param = self.tokenizer.expect(IDENTIFIER)[0]
                self.tokenizer.expect("as")
                type = self.tokenizer.expect(TYPE)[0]
                self.namespace.check_name("var", param)
                self.namespace.check_class("type", type)
                self.namespace.set("var", param, type)
                signature.append(type)
                params.append(Node("PARAM", param))
                if self.tokenizer.match(","):
                    continue
                break
        if self.tokenizer.match(r":\)"):
            self.tokenizer.consume_newline()
            body = Node("BODY", "")
            while not self.tokenizer.end():
                if m := self.tokenizer.match(VARDECL):
                    parsed = self.parse_var_decl(m[1])
                elif m := self.tokenizer.match(RETURN):
                    expr = self.parse_expression()
                    expr_type = self.expression_to_type(expr)
                    if return_type:
                        if return_type != expr_type:
                            raise ParsingError("Mismatching return types")
                    else:
                        return_type = expr_type
                    parsed = Node("RETURN", "", expr)
                elif m := self.tokenizer.match(IDENTIFIER):
                    parsed = self.parse_assignment(m[0])
                elif m := self.tokenizer.match(r":\("):
                    break
                self.tokenizer.consume_newline()
                body.add(parsed)
            else:
                raise ParsingError("Missing sad eyes of function body")

            if not return_type:
                return_type = "void"
            self.namespace.exit_scope()
            self.namespace.set("func", func, [return_type] + signature)
            return Node("FUNCINIT", func, params + [body])
        else:
            if not return_type:
                raise ParsingError("Function without body can't be typeless")
            self.namespace.exit_scope()
            self.namespace.set("func", func, [return_type] + signature)
            return Node("FUNCDECL", func, [Node("RETTYPE", return_type), params])

    def parse_var_decl(self, name):
        self.namespace.check_name("var", name)
        if self.tokenizer.match("is"):
            expr = self.parse_expression()
            type = self.expression_to_type(expr)
            self.namespace.set("var", name, type)
            return Node("VARINIT", name, expr)
        else:
            self.namespace.set("var", name, "")
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
            self.namespace.check_class("var", m[0])
            return Node("VAR", m[0])
        else:
            raise ParsingError("Expected primary")

    def expression_to_type(self, expr: list[Node]):
        # TODO: Actually determining the correct type
        return "int"

    def parse_func_call(self):
        func = self.tokenizer.expect(IDENTIFIER)[0]
        self.namespace.check_class("func", func)
        _, *params = self.namespace.get("func", func)
        if not params:
            self.tokenizer.expect(r"\*")
            return Node("CALL", func)
        self.tokenizer.expect("with")
        args = []
        count = 0
        while True:
            expr = self.parse_expression()
            expr_type = self.expression_to_type(expr)
            if expr_type != params[count]:
                raise ParsingError("Incorrect argument type")
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

    def parse_assignment(self, name: str):
        self.namespace.check_class("var", name)
        self.tokenizer.expect("is")
        expr = self.parse_expression()
        expr_type = self.expression_to_type(expr)
        if self.namespace.get("var", name):
            self.namespace.check_value("var", name, expr_type)
        else:
            self.namespace.set("var", name, expr_type)
        return Node("ASSIGN", name, expr)

    def print_ast(self, node=None, level=0):
        if not node:
            node = self.ast
        print(" " * level + f"{'>' if node.children else '-'} {node}")
        for child in node.children:
            if child:
                self.print_ast(child, level + 2)
