from dataclasses import dataclass
import pandas as pd

DAILY_KEY = 'daily'
WEEKLY_KEY = 'weekly'
MONTHLY_KEY = 'monthly'
YEARLY_KEY = 'yearly'


class Analyst:
    def __init__(self):
        self.table_dict = dict()

    def register(self, table_name: str, csv_file_directory: str):
        try:
            df_file = pd.read_csv(csv_file_directory)
            if isinstance(df_file.index, pd.RangeIndex):
                if df_file.columns.tolist().count('date') == 0:
                    print('Columns should include "date" when indexing was not applied in csv !')
                    return
                df_file.set_index('date', inplace=True)
                df_file.index = pd.to_datetime(df_file.index)
                df_file.sort_index(inplace=True)
            elif isinstance(df_file.index, pd.DatetimeIndex):
                pass
            else:
                print('Table should have either date column or date index !')
                return

        except:
            print('Could read {}'.format(csv_file_directory))
            return

        resample_period_list = {WEEKLY_KEY: '1W', MONTHLY_KEY: '1M', YEARLY_KEY: '1Y'}
        resample_period_key_list = [DAILY_KEY, WEEKLY_KEY, MONTHLY_KEY, YEARLY_KEY]

        table_periods = dict.fromkeys(resample_period_key_list)
        table_periods[DAILY_KEY] = df_file.copy()
        for period in resample_period_key_list[1:]:
            table_periods[period] = df_file.resample(resample_period_list[period]).last()

        self.table_dict.update({table_name: table_periods})
