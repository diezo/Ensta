from unittest import TestCase
import json
from pathlib import Path
from ensta.containers import PostUpload


SUCCESS = Path('./').joinpath('samples/post/success.json')


class PostUploadTest(TestCase):

    def test_parse_success(self):
        with open(SUCCESS) as success:
            success_data = json.load(success)
        post_upload = PostUpload.from_response_data(success_data)
        self.assertIsInstance(post_upload, PostUpload)
        self.assertEqual(post_upload.pk, '3289076043880437691')
