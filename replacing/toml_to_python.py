import tomllib as tl

output_filename = "./tokens_clean.py"

filename = "../tokengen/tokens.toml"
python_syntax = {
    
}

def create_token_list():
    tokens = []
    for key in data:
        for subkey, val in data[key].items():
            tokens.append(val, python_syntax)


def create_python_file():
    file_string = ""
    for key in data:
        file_string += f"# {key}\n"
        for sub_key, val in data[key].items():
            file_string += str(sub_key).upper()
            file_string += " = ["
            for i in range(len(val)-1):
                file_string += f'"{val[i]}", '
            file_string += f'"{val[len(val)-1]}"'
            file_string += "]\n"
        
        file_string += "\n"
    return file_string
            



with open(filename, "rb") as f:
    data = tl.load(f)

for key in data:
    for sub_key, val in data[key].items():
        if not isinstance(val, list):
            data[key][sub_key] = [val]
            

filetext = create_python_file()
with open(output_filename, "w") as f:
    f.write(filetext)
