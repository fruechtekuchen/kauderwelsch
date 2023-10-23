import tomllib as tl

output_filename = "../kauderwelsch/tokens.py"

filename = "tokens.toml"


def create_python_file(table):
    file_string = ""
    for key in data:
        file_string += f"# {key}\n"
        for sub_key, val in data[key].items():
            file_string += str(sub_key).upper()
            file_string += " = \""
            if isinstance(val, list):
                file_string += "\\b("
                for i in range(len(val)-1):
                    file_string += val[i] + "|"
                file_string += val[len(val)-1]
                file_string += ")\\b"
            else:
                file_string += f"\\b({val})\\b"
            file_string += "\"\n"
        file_string += "\n"
    return file_string
            



with open(filename, "rb") as f:
    data = tl.load(f)


filetext = create_python_file(data)
with open(output_filename, "w") as f:
    f.write(filetext)
