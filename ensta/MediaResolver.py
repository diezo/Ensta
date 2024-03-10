
import requests
import tempfile
from pathlib import Path
from urllib.parse import urlparse

class MediaResolver:
    
    def resolve_url(self, url: str):
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            return url
        filename = Path(parsed_url.path).name
        _, file = tempfile.mkstemp(filename)
        response = requests.get(url)
        response.raise_for_status()
        with open(file, 'wb') as output_stream:
            for content in response.iter_content():
                output_stream.write(content)
        return file