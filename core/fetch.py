import datetime

import pandas as pd
from core.constants import TableKey, ANNUAL_TAG, QUARTER_TAG

DATE_KEY: str = 'date'


class Fetcher:
    def __init__(self) -> None:
        self._table_dict = dict()
        pass

    def register(self, key_list: list[TableKey], csv_file_directory: str) -> bool:
        """
        Make pandas Dataframe (table) corresponding to keys in key_list.
        We assume that raw csv has a header contains [symbol, (date), key_list]
        :param key_list: should be contained in the header of csv (will ignore annual/quarter tag
        :param csv_file_directory: created from fmpsdk api call
        :return: true if read successful
        """
        try:
            df_file = pd.read_csv(csv_file_directory)
        except:
            print('cannot read {}.'.format(csv_file_directory))
            return False

        if not df_file.columns.tolist().count(TableKey.Profile.SYMBOL):
            print('no {} column exits.'.format(TableKey.Profile.SYMBOL))
            return False

        if not all(x in df_file.columns.tolist() for x in
                   [key.replace(QUARTER_TAG, "").replace(ANNUAL_TAG, "") for key in key_list]):
            print('not all keys in key list in columns of csv.')
            return False

        is_history_table = df_file.columns.tolist().count(DATE_KEY)
        if (not is_history_table) and (df_file[TableKey.Profile.SYMBOL].duplicated().any()):
            print('Assumed profile table. But duplicated row for a symbol.')
            return False

        if is_history_table:
            df_file.set_index(DATE_KEY, inplace=True)
            df_file.index = pd.DatetimeIndex(df_file.index)
            df_file.sort_index(inplace=True)
            for key in key_list:
                column_name = key.replace(QUARTER_TAG, "").replace(ANNUAL_TAG, "")
                self._table_dict.update(
                    {key: df_file.pivot(columns=TableKey.Profile.SYMBOL, values=column_name)})

        else:
            df_file.index = [0] * len(df_file)
            for key in key_list:
                self._table_dict.update(
                    {key: df_file.pivot(index=None, columns=TableKey.Profile.SYMBOL, values=key)})

        return True

    def query(self, key: TableKey, symbols: list[str], horizon=None) -> pd.DataFrame | None:
        """
        Return table corresponding to key and symbols.
        If horizon is provided as tuple and the key is historical table, return sliced table
        :param key: table key
        :param symbols:
        :param horizon: (date_start, date_end)
        :return:
        """
        if not isinstance(horizon, tuple):
            if isinstance(self._table_dict[key].index, pd.DatetimeIndex):
                print("Queried table is historical table, but no horizon provided! Returning 0th row.")
            return self._table_dict[key].iloc[0][symbols]
        else:
            if isinstance(horizon[0], datetime.date) and isinstance(horizon[1], datetime.date):
                return self._table_dict[key][horizon[0]:horizon[1]][symbols].dropna(how='all')
            else:
                return None
