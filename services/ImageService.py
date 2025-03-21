import requests
from PIL import Image
from io import BytesIO

class ImageService:
    @staticmethod
    def get_image_info(image_url):
        try:
            response = requests.get(image_url)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            return {
                "format": image.format,
                "mode": image.mode,
                "size": image.size,
            }
        except requests.RequestException as e:
            print(e)
            return None