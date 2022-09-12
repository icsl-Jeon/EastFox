import datetime
import unittest
from core.db_interface import DataBaseInterface
from core.constants import TableKey
import time


class DbTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.db_interface = DataBaseInterface()

    def test_profile_table(self):
        print("Getting all profiles..")
        df_table = self.db_interface.get_profile_table(self.db_interface.get_all_symbol_list())
        print(df_table)

    def test_get_history_list(self):
        print("Getting history")
        table_key = TableKey.FinancialRatios.Annual.PER
        table_key = TableKey.MARKET_CAPITALIZATION
        start_time = time.time()
        df_history = self.db_interface.get_history_list(table_key,
                                                        self.db_interface.get_all_symbol_list(),
                                                        datetime.date(1980, 1, 1),
                                                        datetime.date(2022, 1, 1))
        elapsed = (time.time() - start_time)
        print(f"get history elapsed: {elapsed} sec")

        print(df_history)


if __name__ == '__main__':
    unittest.main()
