from unittest import TestCase
import time
from urllib.parse import urlparse
from ensta.MediaResolver import MediaResolver
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
from threading import Thread
from requests import HTTPError

RESOURCES = Path(__file__).parent.joinpath('resources')
MEDIA = RESOURCES.joinpath('media')

class HttpServerTestCase(TestCase):

    root: Path = None
    server_thread: Thread = None
    http_server: HTTPServer = None

    def get_base_url(self):
        return 'http://{}:{}/'.format(
            *self.http_server.server_address
        )
        
    def get_url(self, path: str):
        return self.get_base_url() + path

    @classmethod
    def setUpClass(cls):
        class HttpHandler(SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs) -> None:
                super().__init__(*args, directory=cls.root and str(cls.root.absolute()), **kwargs)

        cls.http_server = HTTPServer(
            ('', 0,),
            HttpHandler,
            bind_and_activate=True,
        )
        cls.server_thread = Thread(target=cls.http_server.serve_forever)
        cls.server_thread.daemon = True
        cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.http_server.shutdown()
        cls.server_thread.join()



class DownloadTest(HttpServerTestCase):
    
    root = MEDIA
    
    media_resolver: MediaResolver
    
    def setUp(self) -> None:
        self.media_resolver = MediaResolver()

    def test_local(self):
        local = './test.txt'
        result = self.media_resolver.resolve_url(local)
        self.assertEqual(result, local)
        
    def test_http(self):
        url = self.get_url('with-content.txt')
        result = self.media_resolver.resolve_url(url)
        with open(result, 'rb') as input_stream:
            self.assertEqual(input_stream.read(), b'ensta')

    def test_empty_http(self):
        url = self.get_url('empty.txt')
        result = self.media_resolver.resolve_url(url)
        with open(result, 'rb') as input_stream:
            self.assertEqual(input_stream.read(), b'')
            
    def test_404(self):
        url = self.get_url('not-found')
        with self.assertRaises(HTTPError):
            self.media_resolver.resolve_url(url)