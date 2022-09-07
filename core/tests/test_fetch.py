import unittest
from core.fetch import Fetcher
from core.constants import *
import pandas as pd
from datetime import date


class FetchTestCase(unittest.TestCase):
    def setUp(self):
        self.fetcher = Fetcher()
        is_profile_registered = self.fetcher.register(get_all_sub_tables(TableKey.Profile),
                                                      '../data/company-profile-20220827.csv')
        is_financial_ratios_registered = self.fetcher.register(get_all_sub_tables(TableKey.FinancialRatios.Annual),
                                                               '../data/financial-ratios-annual-20220819.csv') and \
                                         self.fetcher.register(get_all_sub_tables(TableKey.FinancialRatios.Quarter),
                                                               '../data/financial-ratios-quarter-20220820.csv')
        is_price_history_registered = self.fetcher.register([TableKey.PriceHistory],
                                                            '../data/price-history-20220904.csv')

        self.assertTrue(is_profile_registered)
        self.assertTrue(is_financial_ratios_registered)
        self.assertTrue(is_price_history_registered)

    def test_query(self):
        symbols = ['MMM', 'A', 'TSLA']
        sectors = self.fetcher.query(TableKey.Profile.SECTOR, symbols=symbols)
        industries = self.fetcher.query(TableKey.Profile.INDUSTRY, symbols=symbols)

        horizon = (date(2022, 4, 20), date(2022, 7, 20))
        price_history = self.fetcher.query(TableKey.PriceHistory, symbols=symbols, horizon=horizon)

        self.assertFalse(isinstance(price_history, pd.DataFrame))
        self.assertFalse(isinstance(sectors, pd.DataFrame))
        self.assertFalse(isinstance(industries, pd.DataFrame))

class DbTestCase(unittest.TestCase):
    def setUp(self) -> None:



if __name__ == '__main__':
    unittest.main()
