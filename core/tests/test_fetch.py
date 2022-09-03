import unittest
from core.fetch import Fetcher
from core.constants import *
import pandas as pd


class FetchTestCase(unittest.TestCase):
    def setUp(self):
        self.fetcher = Fetcher()
        is_profile_registered = self.fetcher.register(get_all_sub_tables(TableKey.Profile),
                                                 '../data/company-profile-20220827.csv')
        is_financial_ratios_registered = self.fetcher.register(get_all_sub_tables(TableKey.FinancialRatios.Annual),
                                                          '../data/financial-ratios-annual-20220819.csv') and \
                                         self.fetcher.register(get_all_sub_tables(TableKey.FinancialRatios.Quarter),
                                                          '../data/financial-ratios-quarter-20220820.csv')

        self.assertTrue(is_profile_registered)
        self.assertTrue(is_financial_ratios_registered)

    def test_register(self):
        pass

if __name__ == '__main__':
    unittest.main()
