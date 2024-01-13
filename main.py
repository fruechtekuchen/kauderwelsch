from kauderwelsch.zeh.parser import Parser
from kauderwelsch.zeh.transpiler import Transpiler
import sys
import os

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage main.py <file>")
        exit()
    file = sys.argv[1]
    name, ext = os.path.splitext(file)
    if ext != ".kdw":
        print("Invalid file")
        exit()
    out = name + ".c"
    # if os.path.exists(out):
    #     os.system(f"rm {out}")
    parser = Parser(file)
    parser.parse()
    transpiler = Transpiler(parser.ast, parser.namespace)
    transpiler.transpile()
    transpiler.write(out)
