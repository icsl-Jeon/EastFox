from datetime import datetime
from operator import index
from typing import Dict
import pandas as pd
import datetime


class PropertyNameList:
    PROFILE = 'profile'
    NAME = 'name'
    SYMBOL = 'symbol'
    SECTOR = 'sector'
    SUB_SECTOR = 'subSector'
    PBR = 'priceBookValueRatio'
    PER = 'priceEarningsRatio'
    PCR = 'priceToFreeCashFlowsRatio'
    PSR = 'priceToSalesRatio'
    DIVIDEND_YIELD = 'dividendYield'
    DEBT_RATIO = 'debtRatio'
    MARKET_CAPITALIZATION = 'marketCap'


class PropertyFetcher:
    def __init__(self) -> None:
        self.table_dict = dict()
        pass

        # df_snp500.loc[df_snp500['sector'].isin(['Communication Services', 'Consumer Staples'])].index

    def register(self, key_list: list[str] | str, csv_file_directory: str):
        try:
            df_file = pd.read_csv(csv_file_directory)
        except:
            print('cannot read {}'.format(csv_file_directory))
            return

        if isinstance(key_list, str):
            df_file_transpose = df_file
            self.table_dict.update({key_list: df_file_transpose})
            return

        for key in key_list:
            self.table_dict.update(
                {key: df_file.pivot(index='date', columns='symbol', values=key)})

    def query(self, key: str, symbols: list[str], slice_start_date: str, slice_end_date: str):
        return self.table_dict[key][slice_start_date:slice_end_date][symbols].dropna(how='all')
