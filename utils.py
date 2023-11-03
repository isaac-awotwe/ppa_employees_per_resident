import json

def load_config(file_name):
    with open(file_name) as f:
        data = json.load(f)
    return data