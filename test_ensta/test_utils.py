from unittest import TestCase
import time
from ensta.Utils import time_id


class TimeIdTest(TestCase):

    def test_time_id(self):
        total = 10
        ids = set()
        for _ in range(total):
            ids.add(time_id())
            time.sleep(0.001)
        self.assertEqual(len(ids), total)
