__author__ = 'Shweta'
from django.test import TestCase
from tack.models import Boards
from mock import MagicMock

class BoardTestCase(TestCase):
    def setUp(self):
        Boards.objects.create(Name='B1',privacy='Public')

    def test_board_privacy(self):
        b1 = Boards.objects.get(Name='B1')
        self.assertEqual(b1.privacy, 'Public')



