import json
import requests
import os
import zipfile
import datetime
from google.cloud import storage
from io import BytesIO 
import sys
from PIL import Image
import rarfile
import patoolib
import subprocess
import shutil

def upload_to_gcs(bucket_name, source_file_path, destination_blob_name, credentials_file):
    # Initialize the Google Cloud Storage client with the credentials
    storage_client = storage.Client.from_service_account_json(credentials_file)

    # Get the target bucket
    bucket = storage_client.bucket(bucket_name)

    # Upload the file to the bucket
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_path)
    print(f"File {source_file_path} uploaded to gs://{bucket_name}/{destination_blob_name}")


def process_json_files(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and filename.endswith('.json'):
            with open(file_path, 'r') as file:
                data = json.load(file)
                
            download_urls = [item['download'] for item in data]
            temp_dir = f'temp_{os.path.splitext(filename)[0]}'  # Tạo thư mục tạm thời với tên của file JSON
            os.makedirs(temp_dir, exist_ok=True)
            
            print(f'Downloading... in {download_urls}')
            for url in download_urls:
                response = requests.get(url)
                zip_file = zipfile.ZipFile(BytesIO(response.content))
                zip_file.extractall(temp_dir)
            
            # Lọc và xóa các ảnh nhỏ
            for img_filename in os.listdir(temp_dir):
                img_path = os.path.join(temp_dir, img_filename)
                if img_filename.lower().endswith('.jpeg'):
                    with Image.open(img_path) as img:
                        width, height = img.size
                        size_kb = os.path.getsize(img_path) / 1024  # Size in KB
                        if width < 512 or size_kb < 5:
                            os.remove(img_path)  # Xóa ảnh có kích thước nhỏ
                            print(f"Removed {img_path}")
            
            output_zip = f'{os.path.splitext(filename)[0].replace(" ", "_")}.zip'
            
            with zipfile.ZipFile(output_zip, 'w') as merged_zip:
                for foldername, _, filenames in os.walk(temp_dir):
                    for filename in filenames:
                        if filename.lower().endswith('.jpeg'):
                            file_path = os.path.join(foldername, filename)
                            merged_zip.write(file_path, os.path.relpath(file_path, temp_dir))
            
            # Xóa thư mục tạm thời sau khi tạo file zip
            for file in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, file)
                os.remove(file_path)
            os.rmdir(temp_dir)
            
            print('Download is done!!!!!!!!!!!')
            print("Merged .jpeg files into", output_zip)
            
            # Upload file zip lên Google Cloud Storage
            BUCKET_NAME = "bing_image"
            SOURCE_FILE_PATH = os.path.join(os.getcwd(), output_zip)
            current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            foder_current_time = datetime.datetime.now().strftime("%Y-%m-%d")
            DESTINATION_BLOB_NAME = f'{foder_current_time}/{current_time}_{output_zip}'
            CREDENTIALS_FILE = os.path.join(os.getcwd(), 'charming-layout-405916-805e15076982.json')
            
            upload_to_gcs(BUCKET_NAME, SOURCE_FILE_PATH, DESTINATION_BLOB_NAME, CREDENTIALS_FILE)
            os.remove(SOURCE_FILE_PATH)

def move_file_if_not_exists(src_path, extract_to):
    filename = os.path.basename(src_path)
    target_path = os.path.join(extract_to, filename)
    
    if not os.path.exists(target_path):
        shutil.move(src_path, target_path)
    else:
        print(f"File '{filename}' already exists at the destination '{extract_to}'. Skipping move operation.")


def extract_zip(zip_file_path, extract_to):
    extension = os.path.splitext(zip_file_path)[1].lower()
    if extension == '.zip':
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
            # Di chuyển tất cả các tệp đã giải nén vào thư mục đích
            for root, dirs, files in os.walk(extract_to):
                for file in files:
                    src_path = os.path.join(root, file)
                    # Di chuyển tệp vào thư mục đích
                    move_file_if_not_exists(src_path, extract_to)
                    
    elif extension == '.rar':
        subprocess.run(['unrar', 'x', '-o+', zip_file_path, extract_to])
        # Di chuyển tất cả các tệp đã giải nén vào thư mục đích
        for root, dirs, files in os.walk(extract_to):
            for file in files:
                src_path = os.path.join(root, file)
                # Di chuyển tệp vào thư mục đích
                move_file_if_not_exists(src_path, extract_to)
    else:
        return 'unknown'
    

def main(zip_file_path):
    # Tạo một thư mục tạm thời để giải nén
    temp_extract_folder = 'temp_extract'
    os.makedirs(temp_extract_folder, exist_ok=True)
    
    # Giải nén file zip vào thư mục tạm thời
    extract_zip(zip_file_path, temp_extract_folder)
    
    # Gọi hàm process_json_files với thư mục mới giải nén
    process_json_files(temp_extract_folder)
    
    # # Xóa thư mục tạm thời sau khi hoàn thành
    # for file in os.listdir(temp_extract_folder):
    #     file_path = os.path.join(temp_extract_folder, file)
    #     os.remove(file_path)
    # os.rmdir(temp_extract_folder)
    shutil.rmtree(os.path.join(os.getcwd(), temp_extract_folder))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py path_to_zip_file")
    else:
        zip_file_path = sys.argv[1]
        if not os.path.exists(zip_file_path):
            print("File not found!")
        else:
            main(zip_file_path)











# # Đọc nội dung từ file JSON
# with open('/home/Bing-Creator-Image-Downloader/dataset_bulk-image-downloader_2023-12-11_06-40-20-768.json', 'r') as file:
#     data = json.load(file)

# # Lấy các đường dẫn download từ dữ liệu JSON
# download_urls = [item['download'] for item in data]

# # Tạo thư mục tạm thời để lưu trữ các file
# temp_dir = 'temp_dir'
# os.makedirs(temp_dir, exist_ok=True)

# print(f'Downloading... in {download_urls}')
# # Tải các file zip từ các đường dẫn download và lưu vào thư mục tạm thời
# for url in download_urls:
#     response = requests.get(url)
#     zip_file = zipfile.ZipFile(BytesIO(response.content))
#     zip_file.extractall(temp_dir)

# # Tạo file zip mới để gộp các file đã tải về
# output_zip = 'merged_files.zip'
# with zipfile.ZipFile(output_zip, 'w') as merged_zip:
#     for foldername, _, filenames in os.walk(temp_dir):
#         for filename in filenames:
#             if filename.lower().endswith('.jpeg'):
#                 file_path = os.path.join(foldername, filename)
#                 merged_zip.write(file_path, os.path.relpath(file_path, temp_dir))

# # Xóa thư mục tạm thời
# for file in os.listdir(temp_dir):
#     file_path = os.path.join(temp_dir, file)
#     os.remove(file_path)
# os.rmdir(temp_dir)

# print('Download is done!!!!!!!!!!!')
# print("Merged .jpeg files into", output_zip)
# BUCKET_NAME = "bing_image"
# SOURCE_FILE_PATH = os.path.join(os.getcwd(), output_zip)
# current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# DESTINATION_BLOB_NAME = f'{current_time}_{output_zip}'
# CREDENTIALS_FILE = os.path.join(os.getcwd(), 'charming-layout-405916-b11d4529258e.json')
    
# upload_to_gcs(BUCKET_NAME, SOURCE_FILE_PATH, DESTINATION_BLOB_NAME, CREDENTIALS_FILE)
