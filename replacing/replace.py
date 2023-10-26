import tokens_clean

input_file = "../example.kdw"
output_file = "example.py"


with open(input_file, "r") as f:
    file = f.read()


lines = file.splitlines()
for line in lines:
    print(line)
