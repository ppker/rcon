"""Tests the configuration file parsing."""

from itertools import product
from random import shuffle
from string import printable
from typing import Iterator, Tuple
from unittest import TestCase

from rcon.config import Config


class TestConfig(TestCase):
    """Test the named tuple Config."""

    def setUp(self):
        """Sets up test and target data."""
        chars = list(printable)
        shuffle(chars)
        self.passwd = ''.join(chars)
        self.hosts = [
            'subsubdomain.subdomain.example.com',
            'locahost',
            '127.0.0.1'
        ]
        self.ports = range(65_536)

    @property
    def sockets(self) -> Iterator[Tuple[str, int]]:
        """Yields (host, port) tuples."""
        return product(self.hosts, self.ports)

    def test_from_string(self):
        """Tests the Config.from_string() method."""
        for host, port in self.sockets:
            config = Config.from_string(f'{host}:{port}')
            self.assertEqual(config.host, host)
            self.assertEqual(config.port, port)
            self.assertIsNone(config.passwd)
            config = Config.from_string(f'{self.passwd}@{host}:{port}')
            self.assertEqual(config.host, host)
            self.assertEqual(config.port, port)
            self.assertEqual(config.passwd, self.passwd)