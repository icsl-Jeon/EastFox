from datetime import datetime
from operator import index
from typing import Dict
import pandas as pd
import datetime

date_key = 'date'
symbol_key = 'symbol'


class Fetcher:
    def __init__(self) -> None:
        self.table_dict = dict()
        self.date_index_dict = dict()
        pass

    def register(self, key_list: list[str], csv_file_directory: str):
        try:
            df_file = pd.read_csv('financial-ratios-20220819.csv')
        except:
            print('cannot read {}'.format(csv_file_directory))
            return

        for key in key_list:
            self.table_dict.update(
                {key: df_file.pivot(index='date', columns='symbol', values=key)})
            self.date_index_dict.update(
                {key: self.table_dict[key].index.tolist()})

    def fetch_past(self, key: str, symbol: str, query_date: datetime.date, horizon: int,
                   reverse_search_idx_hint: None | int) -> tuple[pd.Series, int]:
        history_date = list(self.date_index_dict[key])
        history_value = list(self.table_dict[key][symbol])

        assert len(history_date) == len(history_value)

        if reverse_search_idx_hint:
            index_end = reverse_search_idx_hint + 1
        else:
            index_end = len(history_date)

        index_start = 0

        collected_date = []
        collected_value = []

        keep_first_found_idx = True
        first_search_from_back = index_end

        for idx in reversed(range(index_start, index_end)):
            date = history_date[idx]
            value = history_value[idx]

            if date <= query_date:
                if keep_first_found_idx:
                    first_search_from_back = idx
                    keep_first_found_idx = False
                if value == value:
                    collected_date.append(date)
                    collected_value.append(value)

            if len(collected_date) > horizon - 1:
                break

        return pd.Series(collected_value, index=collected_date, dtype=float), first_search_from_back
