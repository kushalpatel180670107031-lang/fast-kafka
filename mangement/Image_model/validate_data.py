import requests 
from PIL import Image
from io import BytesIO

def is_valid_image(url):
    try:
        response = requests.head(url, timeout=10)
        if response.status_code != 200:
            return False
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            return False
        return True
    except:
        return False      

def download_image(url, save_path):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            img.save(save_path)
            return True
    except:
        return False
    return False