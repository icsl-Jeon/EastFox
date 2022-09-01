import unittest
from core.fetch import Fetcher
from core.constants import *
import pandas as pd


class FetchTestCase(unittest.TestCase):
    def test_profile(self):
        fetcher = Fetcher()
        self.assertTrue(fetcher.register([TableKey.Profile.SECTOR, TableKey.Profile.SYMBOL],
                                         '../data/company-profile-20220827.csv'))


if __name__ == '__main__':
    unittest.main()
