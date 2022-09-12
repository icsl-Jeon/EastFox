import datetime
import threading
import unittest
from core.constants import TableKey
from core.strategy import Selector, SelectorType, SelectorSequence, Filter
from datetime import date
from core.db_interface import DataBaseInterface
from core.strategy import Strategist
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
import time


class CentileSimulation(unittest.TestCase):
    def setUp(self) -> None:
        self.db_interface = DataBaseInterface()
        self.exchange_pool = ['NYSE','NASDAQ']
        self.horizon = (date(2000, 1, 1), date(2022, 8, 22))
        self.n_division = 5
        self.freq = '6M'

        pass

    def test_per(self):
        target_key = TableKey.FinancialRatios.Annual.PER
        lookback_year = 2

        filter_list = []
        relative_range_list = [(i / self.n_division, (i + 1) / self.n_division) for i in range(self.n_division)]
        relative_range_list.append((0.0, 1.0))

        for relative_value_range in relative_range_list:
            filter_name = target_key + '=(' + str(relative_value_range[0]) + '-' + str(relative_value_range[1]) + ')'
            relative_selector = Selector(type=SelectorType.HORIZON_RANGE, key=target_key, value=relative_value_range,
                                         horizon=lookback_year,
                                         is_absolute=False)
            selector_sequence = SelectorSequence(selectors=[relative_selector])
            filter_list.append(Filter(selector_sequence_union=[selector_sequence], name=filter_name))

        initial_symbols = self.db_interface.get_stock_on_exchange(self.exchange_pool)
        rebalance_dates = pd.date_range(self.horizon[0], self.horizon[1], freq=self.freq, inclusive='both')
        strategist_list = []
        for filter_ in filter_list:
            strategist_name = filter_.name

            strategist = Strategist(fetcher=self.db_interface, name=strategist_name, asset_pool=initial_symbols,
                                    start_date=self.horizon[0], end_date=self.horizon[1])
            for rebalance_date in rebalance_dates:
                start_time = time.time()
                strategist.apply_filter(filter_in=filter_, date_in=rebalance_date.date())
                elapsed = (time.time() - start_time)
                print(f"\nApplying filter elapsed: {elapsed} sec")

            strategist_list.append(strategist)


if __name__ == '__main__':
    unittest.main()
