from unittest import TestCase
import json
from pathlib import Path
from ensta.containers import ReelUpload


SUCCESS = Path('./').joinpath('samples/reel/success.json')


class ReelUploadTest(TestCase):

    def test_parse_success(self):
        with open(SUCCESS) as success:
            success_data = json.load(success)
        reel_upload = ReelUpload.from_response_data(success_data)
        self.assertIsInstance(reel_upload, ReelUpload)
        self.assertEqual(reel_upload.pk, '3289102505917171189')
