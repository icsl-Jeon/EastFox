import unittest
from core.constants import TableKey
from datetime import date
from core.db_interface import DataBaseInterface
from pytictoc import TicToc


class FetchSimulation(unittest.TestCase):
    def setUp(self) -> None:
        self.db_interface = DataBaseInterface()
        self.exchange_pool = ['NYSE', 'NASDAQ']
        self.horizon = (date(2020, 1, 1), date(2022, 8, 22))
        self.n_division = 5
        self.freq = '6M'

        pass

    def test_fetch_symbols(self):
        t = TicToc()
        t.tic()
        symbol_list = self.db_interface.get_stock_on_exchange(self.exchange_pool)
        t.toc()
        print(symbol_list)

    def test_past_average_filter(self):
        t = TicToc()
        table_key = TableKey.MARKET_CAPITALIZATION
        table_key = TableKey.FinancialRatios.Annual.PER
        from_date = '2020-01-01'
        to_date = '2022-01-01'
        symbol_list = self.db_interface.get_stock_on_exchange(self.exchange_pool)
        symbols_before_filtering = len(symbol_list)
        t.tic()
        symbol_list = self.db_interface.past_average_filter(symbol_list=symbol_list,
                                                            table_key=table_key,
                                                            from_date=from_date, to_date=to_date,
                                                            lower=0.9, upper=1.0)
        testing_summary = f"Filtering from {table_key} over ({from_date, to_date}) from {symbols_before_filtering} stocks took"
        t.toc(testing_summary)
        print(symbol_list)

    def test_price_history(self):
        table_key = TableKey.PRICE_HISTORY
        symbol_list = self.db_interface.get_stock_on_exchange(self.exchange_pool)
        t = TicToc()
        t.tic()
        df_table_output = \
            self.db_interface.get_history_list(table_key=table_key, symbol_list=['A'],
                                               from_date='2000-01-01',to_date='2010-01-01')
        t.toc()


if __name__ == '__main__':
    unittest.main()
