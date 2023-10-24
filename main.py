from kauderwelsch.parser import RDParser
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
    out = name + ".kdw.py"
    # if os.path.exists(out):
    #     os.system(f"rm {out}")
    parser = RDParser(file)
    parser.parse()
    parser.write(out)
