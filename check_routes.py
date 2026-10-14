with open("server.py", "r") as f:
    for line in f:
        if "@app." in line:
            print(line.strip())
