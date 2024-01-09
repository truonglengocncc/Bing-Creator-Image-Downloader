import os
import subprocess 
import sys
import toml
import time 

file_path = os.path.join(os.getcwd(), 'collection.txt')
config_file = os.path.join(os.getcwd(), 'config.toml')

collections = []
with open(file_path, 'r') as file:
    for line in file:
        collections.append(line.strip())  

command = ["python", "main.py"]

# Đọc cấu hình gốc
with open(config_file, 'r') as file:
    config = toml.load(file)

for collection in collections:
    # Thêm collection mới vào danh sách
    config['collection']['collections_to_include'].append(collection)
    
    # Ghi cấu hình mới vào file
    with open(config_file, 'w') as file:
        toml.dump(config, file)
    
    # Thực hiện tiến trình với cấu hình mới
    subprocess.run(command)
    # Xóa hết dữ liệu trong danh sách collections_to_include
    config['collection']['collections_to_include'] = []
    
