from __future__ import annotations
from dataclasses import dataclass, field
from enum import StrEnum, auto
import re

VARDEC = "noob"
FUNCDEC = "diy"
RETURN = "yeet"

PRINT = "lol"
EXIT = "kys"
SLEEP = "afk"

KEYWORDS = [VARDEC, FUNCDEC, RETURN]
WHITESPACE = r"\s+"
SPECIAL = f"(i?)\b({PRINT}|{EXIT}|{SLEEP})\b"
IDENTIFIER = r"\b\w+\b"
VALUE = r"\b[+-]?\d+\b"


class NodeType(StrEnum):
    ROOT = auto()
    VARDEC = auto()


@dataclass
class Node:
    node_type: NodeType
    value: str = ""
    children: list[Node] = field(default_factory=list)

    def __repr__(self):
        return f"Node(type: {self.node_type.name}, value: {self.value!r}, children: {len(self.children)})"


def expect(string, pattern):
    pass


def parse_vardec(code, node):
    pass


def parse_keyword(code, keyword, node: Node):
    if keyword == "noob":
        new_node = Node(NodeType.VARDEC)
        parse_vardec(code, new_node)
        node.children.append(new_node)
    elif keyword == "diy":
        pass
    else:
        print(f"Unexpected keyword '{keyword}'")
        exit()
    return 0


def parse_special(code, name, node):
    return 0


def parse_identifier(code, identifier, node):
    return 0


def parse(code):
    ast = Node(NodeType.ROOT)
    pointer = 0
    l = 0
    while pointer < len(code):
        if m := re.match(WHITESPACE, code[pointer:]):
            l = m.end()
        elif m := re.match(KEYWORDS, code[pointer:]):
            pointer += m.end()
            l = parse_keyword(code[pointer:], m[0].lower(), ast)
        elif m := re.match(SPECIAL, code[pointer:]):
            pointer += m.end()
            l = parse_special(code[pointer:], m[0].lower(), ast)
        elif m := re.match(IDENTIFIER, code[pointer:]):
            pointer += m.end()
            l = parse_identifier(code[pointer:], m[0], ast)
        else:
            print(f"Unable to parse at {pointer} -> '{code[pointer:pointer+20]}'")
            return
        pointer += l
    return ast


code = """
noob x is 4
"""
ast = parse(code)
print(ast)
