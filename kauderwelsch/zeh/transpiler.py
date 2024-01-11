from .parser import Node
from .errors import TranspilationError

OP_TRANS = {"w/": "+", "w/o": "-", "x": "*", "/": "/"}


class Transpiler:
    def __init__(self, ast: Node, scopes: dict[str, dict]):
        self.ast = ast
        self.scopes = scopes
        self.current_scope = self.scopes["root"]
        self.globals = self.scopes["global"]
        self.buffer = ""
        self.indent = 0

    def get(self, key: str):
        if o := self.current_scope.get(key, None):
            return o
        if o := self.globals.get(key, None):
            return o
        raise TranspilationError("Unknown identifer")

    def add(self, node: Node):
        match node.type:
            case "VARDECL":
                body = self.build_var_decl(node)
            case "VARINIT":
                body = self.build_var_init(node)
            case "PARAN":
                pass
            case "ASSIGN":
                body = self.build_assign(node)
            case "FUNCDECL":
                pass
            case "CALL":
                body = self.build_func_call()
        self.add_line(body)

    def transpile(self):
        for child in self.ast.children:
            self.add(child)

    def add_line(self, line: str):
        self.buffer += "\t" * self.indent + line + ";\n"

    def build_var_decl(self, var: Node) -> str:
        return f"{self.get(var.value)} {var.value}"

    def build_var_init(self, var: Node) -> str:
        return (
            f"{self.get(var.value)} {var.value} = {self.build_expression(var.children)}"
        )

    def build_assign(self, var: Node) -> str:
        return f"{var.value} = {self.build_expression(var.children)}"

    def build_expression(self, nodes: list[Node]) -> str:
        expr = ""
        for node in nodes:
            match node.type:
                case "VAR":
                    expr += node.value
                case "LITERAL":
                    expr += node.value
                case "OPERATOR":
                    expr += OP_TRANS[node.value]
                case "PARAN":
                    expr += f"({self.build_expression(node.children)})"
                case "CALL":
                    expr += self.build_func_call(node)
            expr += " "
        return expr[:-1]

    def build_func_call(self, func: Node) -> str:
        call = f"{func.value}("
        for arg in func.children:
            call += self.build_expression(arg.children) + ","
        if call[-1] == ",":
            call = call[:-1]
        return call + ")"

    def write(self, file: str):
        with open(file, "w") as f:
            f.write(self.buffer)
