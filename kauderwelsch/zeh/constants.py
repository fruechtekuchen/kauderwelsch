VARDECL = r"noob\s+(\w+)"
FUNCDECL = "diy"
RETURN = "yeet"
WHILE = "fruitloop"

PRINT = "lol"
EXIT = "kys"
SLEEP = "afk"

FUNCCALL = r"\*"

KEYWORDS = f"\\b({VARDECL}|{RETURN}|{FUNCDECL}|{WHILE})"
WHITESPACE = r"\s+"
SPECIAL = f"(i?)\b({PRINT}|{EXIT}|{SLEEP})\b"
IDENTIFIER = r"\w+"
VALUE = r"\b[+-]?\d+\b"
OPERATORS = r"w/o|w/|x|/"

OP_TRANS = {
    "w/o": "-",
    "w/": "+",
    "x": "*",
    "/": "/",
}

RESERVED = [
    "noob",
    "diy",
    "yeet",
    "lol",
    "kys",
    "afk",
    "is",
    "with",
    "x",
]
TYPE = r"\w+\*?"

S_GLOBAL = "0"
S_ROOT = "1"
