import os
import math
import requests
import uuid
from settings import load_settings

def upload_file(file_path):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return False, f"Файл {file_path} не существует или пуст."

    settings = load_settings()
    api_key = settings.get('api_key')
    if not api_key:
        return False, "API key is not set."

    id = str(uuid.uuid4())
    file_size = os.path.getsize(file_path)
    chunk_size = 20 * 1024 * 1024  # 20 MB chunk size
    total_chunks = math.ceil(file_size / chunk_size)

    try:
        with open(file_path, 'rb') as file:
            chunk_number = 0
            while True:
                chunk = file.read(chunk_size)
                if not chunk:
                    break  # Reached EOF

                # Construct the request parameters
                data = {
                    'api_key': api_key,
                    'id': id,
                    'chunk_number': chunk_number,
                    'chunk_total': total_chunks,
                    'filename': os.path.basename(file_path),
                }

                # Send the chunk as part of the request
                files = {'file': chunk}
                response = requests.post("https://backend.mymeet.ai/api/video", data=data, files=files)
                response.raise_for_status()

                print(response.text)
                chunk_number += 1

        return True, "File successfully uploaded."
    except requests.exceptions.RequestException as e:
        return False, f"Upload failed: {e}"
