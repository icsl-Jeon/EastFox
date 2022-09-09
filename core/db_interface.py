import datetime
import os
import ssl
import time

from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select
from sqlalchemy import inspect, types
from sqlalchemy.dialects.mysql import insert

from urllib.request import urlopen
import urllib.parse
import certifi
import json
from aenum import StrEnum, skip, auto
from tqdm import tqdm

import pandas as pd
from dataclasses import dataclass

import core.constants
from core.constants import TableKey, TableValue, get_all_sub_tables

load_dotenv()
DB_USERNAME = os.environ.get("sql_user")
DB_PASSWORD = os.environ.get("sql_password")
DB_NAME = os.environ.get("sql_db_name")
DB_IP = os.environ.get("sql_ip")
DB_PORT = os.environ.get("sql_port")
API_KEY = os.environ.get("apikey")

PERIOD_TAG_LIST = [core.constants.ANNUAL_TAG[1:], core.constants.QUARTER_TAG[1:]]


def get_jsonparsed_data(url):
    ssl_context = ssl.create_default_context()
    response = urlopen(url, context=ssl_context)
    data = response.read().decode("utf-8")
    return json.loads(data)


def call_fmp_api(version: int, api_name: str, params: dict, ) -> list:
    api_str = "".join(
        ['https://financialmodelingprep.com/api/',
         f'v{version}/',
         api_name, '?',
         urllib.parse.urlencode(params)])

    result = get_jsonparsed_data(api_str)
    return result


class TableName(StrEnum):
    PROFILE = "profile"
    FINANCIAL_RATIO_ANNUAL = "financial_ratio_annual"
    FINANCIAL_RATIO_QUARTER = "financial_ratio_quarter"


@dataclass
class CallArgument:
    version: int
    api_name: str
    symbol_required: bool
    default_param: dict


FMP_API = dict({
    TableName.FINANCIAL_RATIO_ANNUAL:
        CallArgument(3, 'ratios', True, {'period': 'annual', 'limit': 500, 'apikey': API_KEY}),
    TableName.FINANCIAL_RATIO_QUARTER:
        CallArgument(3, 'ratios', True, {'period': 'quarter', 'limit': 500, 'apikey': API_KEY})
})


class DataBaseInterface:

    def __init__(self):
        db_url = f"mariadb+mariadbconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_IP}:{DB_PORT}/{DB_NAME}?use_unicode=1&charset=utf8"
        self._engine = create_engine(db_url, pool_pre_ping=True, pool_recycle=3600)
        self._conn = self._engine.connect()
        self._table_dict = dict()
        self._meta = MetaData()
        self._meta.reflect(self._conn)
        self._inspector = inspect(self._engine)

        for table in self._meta.tables:
            tag = ""
            if table.split('_')[-1] in PERIOD_TAG_LIST:
                tag = '_' + table.split('_')[-1]
            self._table_dict.update({table: [str(key) + tag for key in self._meta.tables[table].columns.keys()]})

    def __is_table_exist(self, table_name: str) -> bool:
        return table_name in self._inspector.get_table_names()

    def __get_column_types(self, result_dict: dict) -> dict:
        column_types = {}
        for k, v in result_dict.items():
            python_type = type(v)
            if k == TableKey.Profile.SYMBOL:
                sql_type = types.VARCHAR(50)
            elif k == 'date':
                sql_type = types.DATE()
            elif python_type == str:
                sql_type = types.TEXT()
            else:
                sql_type = types.FLOAT()
            column_types.update({k: sql_type})

        return column_types

    def __insert_table(self, table_name: str, values: list, columns) -> bool:
        table = Table(table_name, self._meta, *columns,
                      extend_existing=True)
        self._meta.create_all(self._engine)
        try:
            stmt = insert(table).values(values)
            update_dict = {x.name: x for x in stmt.inserted}
            on_duplicate_key_stmt = stmt.on_duplicate_key_update(update_dict)
            self._conn.execute(statement=on_duplicate_key_stmt)
            return True

        except:
            return False

    def __set_primary_key(self, table_name: str, key_column: str, additional_key_column=None) -> bool:
        if not additional_key_column:
            sql = f"alter table {table_name} add primary key({key_column})"
        else:
            sql = f"alter table {table_name} add primary key({key_column},{additional_key_column})"
        try:
            self._conn.execute(sql)
            return True
        except:
            return False

    def get_all_symbol_list(self) -> list[str]:
        existing_symbols = []
        if TableName.PROFILE in self._meta.tables:
            s = select(self._meta.tables[TableName.PROFILE].c[TableKey.Profile.SYMBOL])
            existing_symbols = [row[0] for row in self._conn.execute(s)]
        return existing_symbols

    def update_profile_table(self, target_exchange_list: list) -> bool:
        table_name = TableName.PROFILE
        existing_symbols = self.get_all_symbol_list()

        result = call_fmp_api(3, 'stock/list', {'apikey': API_KEY})
        if len(result) == 0:
            return False

        all_column_types = self.__get_column_types(result[0])
        target_columns = (Column(TableKey.Profile.SYMBOL, types.VARCHAR(20), primary_key=True),
                          Column(TableKey.Profile.NAME, types.TEXT()),
                          Column(TableKey.Profile.SECTOR, types.VARCHAR(200)),
                          Column(TableKey.Profile.INDUSTRY, types.TEXT()),
                          Column(TableKey.Profile.EXCHANGE, types.VARCHAR(20)),
                          Column(TableKey.Profile.TYPE, types.VARCHAR(20)))

        print("Starting upload to db..")
        for item in tqdm(result):
            if item[TableKey.Profile.SYMBOL] in existing_symbols or \
                    item[TableKey.EXCHANGE] not in target_exchange_list:
                continue

            profile_result = call_fmp_api(3, f'profile/{item[TableKey.Profile.SYMBOL]}', {'apikey': API_KEY})

            target_element = {k: item[k] for k in get_all_sub_tables(TableKey.Profile) if
                              k in list(all_column_types.keys())}
            target_element.update(
                {str(k): profile_result[0][k] for k in [TableKey.Profile.INDUSTRY, TableKey.Profile.SECTOR]})

            if not self.__insert_table(table_name, [target_element], target_columns):
                continue

        return True

    def __get_historical_table(self, table_name: TableName, symbol_list: list[str]) -> pd.DataFrame | None:
        if not self.__is_table_exist(table_name):
            return None
        table = self._meta.tables[table_name]
        s = select(table).where(table.c[TableKey.Profile.SYMBOL].in_(symbol_list))
        return pd.DataFrame(self._conn.execute(s).fetchall())

    def __is_table_latest_enough(self, table_name: TableName, symbol: str, allowable_days: datetime.timedelta) -> bool:
        if not self.__is_table_exist(table_name):
            return False

        table = self._meta.tables[table_name]
        s = select(table.c['date']).where(table.c[TableKey.Profile.SYMBOL] == symbol)
        result = [item[0] for item in self._conn.execute(s).fetchall()]

        if not result:
            return False
        today = datetime.date.today()
        return (today - max(result)) < allowable_days

    def __get_allowable_days_criteria(self, table_name: TableName) -> datetime.timedelta:
        if table_name == TableName.FINANCIAL_RATIO_QUARTER:
            return datetime.timedelta(days=30 * 3)
        elif table_name == TableName.FINANCIAL_RATIO_ANNUAL:
            return datetime.timedelta(days=30 * 12)
        else:
            return datetime.timedelta(days=30 * 1)

    def __call_fmp_api_for_table(self, table_name: TableName, symbol=None):
        table_api: CallArgument = FMP_API[table_name]
        query_url_base = table_api.api_name

        url_combination = [query_url_base, ]
        if table_api.symbol_required:
            url_combination.append(symbol)
        api_url = "/".join(url_combination)
        return call_fmp_api(table_api.version, api_url, table_api.default_param)

    def update_historical_table(self, table_name: TableName):
        should_set_primatry_key = not self.__is_table_exist(table_name)

        symbol_list = self.get_all_symbol_list()
        tqdm_position = list(vars(TableName)['_value2member_map_'].keys()).index(table_name)
        for symbol in tqdm(symbol_list):
            if self.__is_table_latest_enough(table_name, symbol,
                                             self.__get_allowable_days_criteria(table_name)):
                continue

            result = self.__call_fmp_api_for_table(table_name, symbol)
            if len(result) == 0:
                continue

            all_column_types = self.__get_column_types(result[0])
            columns = (Column(k, v, primary_key=(k == 'symbol' or k == 'date')) for k, v in all_column_types.items())
            if not self.__insert_table(table_name, result, columns):
                continue

            if should_set_primatry_key:
                sql = f"alter table {table_name} add primary key(symbol,date)"
                self._conn.execute(sql)
                should_set_primatry_key = False

    def update(self, renew_profile_table=False):
        if renew_profile_table:
            db_interface.update_profile_table([TableValue.Exchange.NYSE,
                                               TableValue.Exchange.NASDAQ,
                                               TableValue.Exchange.AMEX])

        self.update_historical_table(TableName.FINANCIAL_RATIO_QUARTER)
        self.update_historical_table(TableName.FINANCIAL_RATIO_ANNUAL)

    def __find_table_name(self, table_key: TableKey) -> str | None:
        table_name = None
        for k, v in self._table_dict.items():
            if table_key in v:
                table_name = k
                break
        return table_name

    def get_history_list(self, table_key: TableKey, symbol_list=list[str]) -> pd.DataFrame | None:
        table_name = self.__find_table_name(table_key)
        if not table_name:
            return None

        table_selected = self._meta.tables[table_name]
        if table_key.split('_')[-1] in PERIOD_TAG_LIST:
            table_key = "_".join(table_key.split('_')[0:-1])

        s = select(
            [table_selected.c['date'], table_selected.c[TableKey.Profile.SYMBOL], table_selected.c[table_key]]).where(
            table_selected.c[TableKey.Profile.SYMBOL].in_(symbol_list))
        df_table = pd.DataFrame(self._conn.execute(s).fetchall())
        df_table.set_index('date', inplace=True)
        df_table.index = pd.DatetimeIndex(df_table.index)
        return df_table.pivot(columns=TableKey.Profile.SYMBOL, values=table_key)

import time

if __name__ == "__main__":
    db_interface = DataBaseInterface()
    # db_interface.update()
    start_time = time.time()
    table = db_interface.get_history_list(TableKey.FinancialRatios.Annual.PER, db_interface.get_all_symbol_list())
    elapsed = (time.time() - start_time)
    print(elapsed)

    pass
