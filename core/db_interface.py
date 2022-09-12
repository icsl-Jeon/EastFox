import datetime
import os
import ssl
import threading
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select
from sqlalchemy import inspect, types
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import and_

from urllib.request import urlopen
import urllib.parse
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
    INCOME_STATEMENT_ANNUAL = "income_statement_annual"
    INCOME_STATEMENT_QUARTER = "income_statement_quarter"
    BALANCE_SHEET_ANNUAL = "balance_sheet_annual"
    BALANCE_SHEET_QUARTER = "balance_sheet_quarter"
    CASHFLOW_ANNUAL = "cashflow_annual"
    CASHFLOW_QUARTER = "cashflow_quarter"
    MARKET_CAPITALIZATION = "market_capitalization"
    DAILY_PRICE = "daily_price"


@dataclass
class CallArgument:
    version: int
    api_name: str
    symbol_required: bool
    default_param: dict


today = datetime.date.today().strftime("")

FMP_API = dict({
    TableName.FINANCIAL_RATIO_ANNUAL:
        CallArgument(3, 'ratios', True, {'period': 'annual', 'limit': -1, 'apikey': API_KEY}),
    TableName.FINANCIAL_RATIO_QUARTER:
        CallArgument(3, 'ratios', True, {'period': 'quarter', 'limit': -1, 'apikey': API_KEY}),
    TableName.INCOME_STATEMENT_QUARTER:
        CallArgument(3, 'income-statement', True, {'period': 'quarter', 'limit': -1, 'apikey': API_KEY}),
    TableName.INCOME_STATEMENT_ANNUAL:
        CallArgument(3, 'income-statement', True, {'period': 'annual', 'limit': -1, 'apikey': API_KEY}),
    TableName.BALANCE_SHEET_ANNUAL:
        CallArgument(3, 'balance-sheet-statement', True, {'period': 'annual', 'limit': -1, 'apikey': API_KEY}),
    TableName.BALANCE_SHEET_QUARTER:
        CallArgument(3, 'balance-sheet-statement', True, {'period': 'quarter', 'limit': -1, 'apikey': API_KEY}),
    TableName.CASHFLOW_ANNUAL:
        CallArgument(3, 'cash-flow-statement', True, {'period': 'annual', 'limit': -1, 'apikey': API_KEY}),
    TableName.CASHFLOW_QUARTER:
        CallArgument(3, 'cash-flow-statement', True, {'period': 'quarter', 'limit': -1, 'apikey': API_KEY}),
    TableName.MARKET_CAPITALIZATION:
        CallArgument(3, 'historical-market-capitalization', True, {'limit': -1, 'apikey': API_KEY}),
    TableName.DAILY_PRICE:
        CallArgument(3, 'historical-price-full', True, {'from': '1980-01-01', 'apikey': API_KEY}),
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
        self._session_maker = sessionmaker(self._engine)
        self._update_report = dict()

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

    def __insert_table(self, table_name: str, values: list, columns, session=None) -> bool:
        table = Table(table_name, self._meta, *columns,
                      extend_existing=True)
        self._meta.create_all(self._engine)
        try:
            stmt = insert(table).values(values)
            update_dict = {x.name: x for x in stmt.inserted}
            on_duplicate_key_stmt = stmt.on_duplicate_key_update(update_dict)
            if not session:
                self._conn.execute(statement=on_duplicate_key_stmt)
            else:
                session.execute(statement=on_duplicate_key_stmt)
                session.commit()
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

    def get_all_symbol_list(self, session=None) -> list[str]:
        existing_symbols = []
        if TableName.PROFILE in self._meta.tables:
            s = select(self._meta.tables[TableName.PROFILE].c[TableKey.Profile.SYMBOL])
            if not session:
                existing_symbols = [row[0] for row in self._conn.execute(s)]
            else:
                existing_symbols = [row[0] for row in session.execute(s)]

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

    def is_table_latest_enough(self, table_name: TableName, symbol: str, allowable_days: datetime.timedelta,
                               session=None) -> bool:
        if not self.__is_table_exist(table_name):
            return False

        table = self._meta.tables[table_name]
        s = select(table.c['date']).where(table.c[TableKey.Profile.SYMBOL] == symbol)

        if not session:
            date_list = self._conn.execute(s).fetchall()
        else:
            date_list = session.execute(s).fetchall()
            session.close()
        result = [item[0] for item in date_list]

        if not result:
            return False
        today = datetime.date.today()
        return (today - max(result)) < allowable_days

    def __get_allowable_days_criteria(self, table_name: TableName) -> datetime.timedelta:
        if table_name.split('_')[-1] == 'annual':
            return datetime.timedelta(days=30 * 12)
        elif table_name.split('_')[-1] == 'quarter':
            return datetime.timedelta(days=30 * 7)
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

    def update_historical_table(self, table_name: TableName, ):
        session = scoped_session(self._session_maker)
        should_set_primary_key = not self.__is_table_exist(table_name)

        symbol_list = self.get_all_symbol_list(session)
        tqdm_list = tqdm(symbol_list, leave=False)
        tqdm_list.set_description(f"{table_name}")
        for symbol in tqdm_list:
            if self.is_table_latest_enough(table_name, symbol,
                                           self.__get_allowable_days_criteria(table_name),
                                           session):
                continue

            result = self.__call_fmp_api_for_table(table_name, symbol)
            if len(result) == 0:
                continue

            if table_name == TableName.DAILY_PRICE:
                result_temp = []
                for item in result['historical']:
                    result_temp.append({'symbol': symbol, 'date': item['date'], 'adjClose': item['adjClose'],
                                        'volume': item['volume'], 'changePercent': item['changePercent']})
                result = result_temp

            all_column_types = self.__get_column_types(result[0])
            columns = (Column(k, v, primary_key=(k == 'symbol' or k == 'date')) for k, v in all_column_types.items())
            if not self.__insert_table(table_name, result, columns, session):
                continue

            if should_set_primary_key:
                sql = f"alter table {table_name} add primary key(symbol,date)"
                self._conn.execute(sql)
                should_set_primary_key = False
        session.close()

    def __print_progress(self):
        while True:
            [print(f"{table_name}: {report_tuple[0] / report_tuple[1]}") for table_name, report_tuple in
             self._update_report.items()]
            time.sleep(3)

    def update(self, renew_profile_table=False):
        if renew_profile_table:
            self.update_profile_table([TableValue.Exchange.NYSE,
                                       TableValue.Exchange.NASDAQ,
                                       TableValue.Exchange.AMEX])

        table_list = [
            # TableName.INCOME_STATEMENT_ANNUAL, TableName.INCOME_STATEMENT_QUARTER,
            # TableName.FINANCIAL_RATIO_QUARTER, TableName.FINANCIAL_RATIO_ANNUAL,
            # TableName.CASHFLOW_ANNUAL, TableName.CASHFLOW_QUARTER,
            # TableName.BALANCE_SHEET_QUARTER, TableName.BALANCE_SHEET_ANNUAL,
            # TableName.MARKET_CAPITALIZATION,
            TableName.DAILY_PRICE,
        ]

        with ThreadPoolExecutor(len(table_list)) as executor:
            executor.map(self.update_historical_table, table_list)

        # workers = []
        # for table_name in table_list:
        #     worker = threading.Thread(target=self.update_historical_table, args=(table_name,))
        #     worker.start()
        #     workers.append(worker)
        # for worker in workers:
        #     worker.join()

    def __find_table_name(self, table_key: TableKey) -> str | None:
        table_name = None
        for k, v in self._table_dict.items():
            if table_key in v:
                table_name = k
                break
        return table_name

    def get_history_list(self, table_key: TableKey, symbol_list: list[str],
                         from_date: datetime.date,
                         to_date: datetime.date) -> pd.DataFrame | None:
        session = scoped_session(self._session_maker)
        table_name = self.__find_table_name(table_key)
        if not table_name:
            return None

        table_selected = self._meta.tables[table_name]
        if table_key.split('_')[-1] in PERIOD_TAG_LIST:
            table_key = "_".join(table_key.split('_')[0:-1])

        s = select(
            [table_selected.c['date'], table_selected.c[TableKey.Profile.SYMBOL], table_selected.c[table_key]]).where(
            and_((table_selected.c[TableKey.Profile.SYMBOL].in_(symbol_list)),
                 (from_date <= table_selected.c['date']),
                 (to_date >= table_selected.c['date'])))
        df_table = pd.DataFrame(session.execute(s).fetchall())
        session.close()
        if df_table.empty:
            return None

        df_table.set_index('date', inplace=True)
        df_table.index = pd.DatetimeIndex(df_table.index)
        # df_table = df_table.resample('3M').mean()
        df_table_pivot = df_table.pivot(columns=TableKey.Profile.SYMBOL, values=table_key)

        return df_table_pivot

    def get_profile_list(self, table_key: TableKey.Profile, symbol_list: list[str]) -> pd.DataFrame | None:
        session = scoped_session(self._session_maker)
        if not self.__is_table_exist(TableName.PROFILE):
            return None
        if not self.__find_table_name(table_key) == TableName.PROFILE:
            return None

        table_selected = self._meta.tables[TableName.PROFILE]
        s = select([table_selected.c[TableKey.Profile.SYMBOL], table_selected.c[table_key]]). \
            where(table_selected.c[TableKey.Profile.SYMBOL].in_(symbol_list))
        df_table = pd.DataFrame(session.execute(s).fetchall())
        session.close()
        return df_table

    def get_profile_table(self, symbol_list: list[str]) -> pd.DataFrame | None:
        session = scoped_session(self._session_maker)
        if not self.__is_table_exist(TableName.PROFILE):
            return None

        table_selected = self._meta.tables[TableName.PROFILE]
        s = select(['*']).where(table_selected.c[TableKey.Profile.SYMBOL].in_(symbol_list))
        df_table = pd.DataFrame(session.execute(s).fetchall())
        session.close()
        return df_table

    def get_stock_on_exchange(self, exchange_list: list[str]) -> list[str]:
        session = scoped_session(self._session_maker)
        if not self.__is_table_exist(TableName.PROFILE):
            return []

        table_selected = self._meta.tables[TableName.PROFILE]
        s = select([table_selected.c[TableKey.Profile.SYMBOL]]). \
            where(and_(table_selected.c[TableKey.Profile.EXCHANGE].in_(exchange_list),
                       table_selected.c[TableKey.Profile.TYPE] == 'stock'))
        return [item[0] for item in session.execute(s).fetchall()]


import time

if __name__ == "__main__":
    start_time = time.time()
    db_interface = DataBaseInterface()
    db_interface.update(renew_profile_table=False)
    elapsed = (time.time() - start_time)
    print(f"\nElapsed: {elapsed} sec")

    pass
