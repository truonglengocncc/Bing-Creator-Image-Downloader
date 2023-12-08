import os
import subprocess 
import sys
import toml

file_path = os.path.join(os.getcwd(), 'collection.txt')
config_file = os.path.join(os.getcwd(), 'config.toml')

collections = []
with open(file_path, 'r') as file:
    for line in file:
        collections.append(line.strip())  #use strip() to remove space key và enter key

command = ["python", "main.py"]

for collection in collections:
    with open(config_file, 'r') as file:
        config = toml.load(file)
    config['collection']['collections_to_include'].append(collection)
    with open(config_file, 'w') as file:
        toml.dump(config, file)
    subprocess.run(command)
    config['collection']['collections_to_include'].remove(collection)
    with open(config_file, 'w') as file:
        toml.dump(config, file)
