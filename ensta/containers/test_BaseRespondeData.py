from unittest import TestCase
from dataclasses import dataclass
from ensta.containers.BaseRespondeData import BaseRespondeData


class BaseResponseDataTest(TestCase):

    def test_pase_simple_data(self):
        @dataclass
        class SimpleDataclass(BaseRespondeData):
            a: int
            b: float
            c: str

        expected = SimpleDataclass(a=1, b=1., c='1')

        result = SimpleDataclass.from_data({
            'a': 1,
            'b': 1.,
            'c': '1'
        })

        self.assertEqual(result, expected)

    def test_pase_with_dataclass(self):
        @dataclass
        class SimpleDataclass:
            a: int
            b: float
            c: str

        @dataclass
        class WithDataclass(BaseRespondeData):
            dataclass: SimpleDataclass

        expected = WithDataclass(dataclass=SimpleDataclass(a=1, b=1., c='1'))

        result = WithDataclass.from_data({'dataclass': {
            'a': 1,
            'b': 1.,
            'c': '1'
        }})

        print(result)

        self.assertEqual(result, expected)

    def test_pase_with_response_data(self):
        @dataclass
        class SimpleDataclass(BaseRespondeData):
            a: int
            b: float
            c: str

        @dataclass
        class WithDataclass(BaseRespondeData):
            dataclass: SimpleDataclass

        expected = WithDataclass(dataclass=SimpleDataclass(a=1, b=1., c='1'))

        result = WithDataclass.from_data({'dataclass': {
            'a': 1,
            'b': 1.,
            'c': '1'
        }})

        print(result)

        self.assertEqual(result, expected)
