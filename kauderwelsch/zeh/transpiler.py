from .parser import Node, NameSpace
from .errors import TranspilationError
from .constants import *


class Transpiler:
    def __init__(self, ast: Node, namespace: NameSpace):
        self.ast = ast
        self.namespace = namespace
        self.buffer = ""
        self.indent = 0

    def switch_scope(self, name: str):
        self.indent += 1
        self.namespace.switch_scope(name)

    def exit_scope(self):
        self.indent -= 1
        self.namespace.exit_scope()

    def add(self, node: Node):
        match node.type:
            case "VARDECL":
                self.add_var_decl(node)
            case "VARINIT":
                self.add_var_init(node)
            case "ASSIGN":
                self.add_assign(node)
            case "FUNCDECL":
                self.add_line(self.build_func_decl(node) + ";")
            case "FUNCINIT":
                self.add_func_init(node)
            case "CALL":
                self.add_line(self.build_call() + ";")
            case "RETURN":
                self.add_return(node)

    def transpile(self):
        for child in self.ast.children:
            self.add(child)

    def add_line(self, line: str):
        self.buffer += "\t" * self.indent + line + "\n"

    def add_var_decl(self, var: Node) -> str:
        self.add_line(f"{self.namespace.get('var', var.value)} {var.value};")

    def add_var_init(self, var: Node) -> str:
        self.add_line(
            f"{self.namespace.get('var', var.value)} {var.value} = {self.build_expression(var.children)};"
        )

    def add_assign(self, var: Node) -> str:
        self.add_line(f"{var.value} = {self.build_expression(var.children)};")

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
                    expr += self.build_call(node)
            expr += " "
        return expr[:-1]

    def build_call(self, func: Node) -> str:
        call = f"{func.value}("
        for arg in func.children:
            call += self.build_expression(arg.children) + ","
        if call[-1] == ",":
            call = call[:-1]
        return call + ")"

    def build_func_decl(self, func: Node) -> str:
        return_type, *params = self.namespace.get("func", func.value)
        param_list = [p + " " + c.value for p, c in zip(params, func.children)]
        return f"{return_type} {func.value}({','.join(param_list)})"

    def add_func_init(self, func: Node) -> str:
        decl = self.build_func_decl(func)
        self.add_line(decl)
        self.add_line("{")
        self.switch_scope(func.value)
        for node in func.children[-1].children:
            self.add(node)
        self.exit_scope()
        self.add_line("}")

    def add_return(self, node: Node):
        self.add_line(f"return {self.build_expression(node.children)};")

    def write(self, file: str):
        with open(file, "w") as f:
            f.write(self.buffer)
