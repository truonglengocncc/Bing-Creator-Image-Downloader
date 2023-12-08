import os
import subprocess 
import sys
import toml
import copy

file_path = os.path.join(os.getcwd(), 'collection.txt')
config_file = os.path.join(os.getcwd(), 'config.toml')

collections = []
with open(file_path, 'r') as file:
    for line in file:
        collections.append(line.strip())  

command = ["python", "main.py"]

with open(config_file, 'r') as file:
    config = toml.load(file)

original_config = copy.deepcopy(config)  # Tạo bản sao của cấu hình ban đầu

for collection in collections:
    config['collection']['collections_to_include'].append(collection)
    with open(config_file, 'w') as file:
        toml.dump(config, file)
    subprocess.run(command)
    config = copy.deepcopy(original_config)