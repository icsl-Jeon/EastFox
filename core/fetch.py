import pandas as pd
from core.constants import TableKey

DATE_KEY: str = 'date'


class Fetcher:
    def __init__(self) -> None:
        self.table_dict = dict()
        pass

    def register(self, key_list: list[TableKey], csv_file_directory: str) -> bool:
        """
        Make pandas Dataframe (table) corresponding to keys in key_list.
        We assume that raw csv has a header contains [symbol, (date), key_list]
        :param key_list: should be contained in the header of csv
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

        if not all(x in df_file.columns.tolist() for x in key_list):
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
                self.table_dict.update(
                    {key: df_file.pivot(index=DATE_KEY, columns=TableKey.Profile.SYMBOL, values=key)})

        else:
            df_file.index = [0] * len(df_file)
            for key in key_list:
                self.table_dict.update(
                    {key: df_file.pivot(index=None, columns=TableKey.Profile.SYMBOL, values=key)})

        return True

    # def query(self, key: str, symbols: list[str], slice_start_date: str, slice_end_date: str):
    #     return self.table_dict[key][slice_start_date:slice_end_date][symbols].dropna(how='all')
