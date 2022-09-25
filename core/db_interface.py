import datetime
import os
import random
import ssl
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from pandas.api.types import is_numeric_dtype

import time
from sqlalchemy import desc

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
from core.constants import *

load_dotenv()
DB_USERNAME = os.environ.get("sql_user")
DB_PASSWORD = os.environ.get("sql_password")
DB_NAME = os.environ.get("sql_db_name")
DB_IP = os.environ.get("sql_ip")
DB_PORT = os.environ.get("sql_port")
API_KEY = os.environ.get("apikey")

PERIOD_TAG_LIST = [core.constants.ANNUAL_TAG[1:], core.constants.QUARTER_TAG[1:]]  # under score
RESAMPLE_TAG_LIST = [core.constants.ONE_WEEK_AVERAGE_TAG[1:], core.constants.ONE_MONTH_AVERAGE_TAG[1:],
                     core.constants.THREE_MONTH_AVERAGE_TAG[1:], core.constants.ONE_YEAR_AVERAGE_TAG[1:]]
BATCH_SIZE = 150


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


TODAY = datetime.date.today().strftime("")
START_DATE = '1980-01-01'

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
        CallArgument(3, 'historical-price-full', True, {'from': START_DATE, 'apikey': API_KEY}),
})


class DataBaseInterface:

    def __init__(self):
        db_url = f"mariadb+mariadbconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_IP}:{DB_PORT}/{DB_NAME}?use_unicode=1&charset=utf8"
        self._engine = create_engine(db_url, pool_pre_ping=True, pool_recycle=3600, pool_size=20)
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
                tag = '_' + table.split('_')[-1]  # e.g., financial_ratio_annual
            if table.split('_')[-1] in AVERAGE_TAG:
                tag = '_' + table.split('_')[-2] + '_' + table.split('_')[-1]  # e.g., 1m_average

            self._table_dict.update({table: [str(key) + tag for key in self._meta.tables[table].columns.keys()]})

    def __is_table_exist(self, table_name: str) -> bool:
        return inspect(self._engine).has_table(table_name)

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
            if session is None:
                self._conn.execute(statement=on_duplicate_key_stmt)
            else:
                session.execute(statement=on_duplicate_key_stmt)
                session.commit()
            return True

        except Exception as e:
            print({e})
            return False

    def __set_primary_key(self, table_name: str, key_column: str, additional_key_column=None) -> bool:
        if not additional_key_column:
            sql = f"alter table {table_name} add primary key({key_column})"
        else:
            sql = f"alter table {table_name} add primary key({key_column},{additional_key_column})"
        try:
            self._conn.execute(sql)
            return True
        except Exception as e:
            print({e})
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

    def update_profile_table(self, target_exchange_list: list, limit=50000) -> bool:
        table_name = TableName.PROFILE
        existing_symbols = self.get_all_symbol_list()
        result = call_fmp_api(3, 'stock/list', {'apikey': API_KEY})
        if len(result) == 0:
            return False
        result = result[0:limit]
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

    # TODO: deprecated
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

    def __get_latest_date_in_table(self, table_name: TableName, symbol: str, session=None) -> datetime.date:
        old_day = datetime.datetime.strptime(START_DATE, '%Y-%m-%d').date()
        if not self.__is_table_exist(table_name):
            return old_day

        table_selected = self._meta.tables[table_name]

        s = select(table_selected.c['date']).where(table_selected.c[TableKey.Profile.SYMBOL] == symbol).order_by(
            desc(table_selected.c['date'])).limit(1)

        try:
            if session is None:
                result = self._conn.execute(s).fetchall()
            else:
                result = session.execute(s).fetchall()

        except Exception as e:
            print(f"While querying latest data on {symbol} about {table_name}, {e} occurred. Returning old day.")
            return old_day

        if not result:
            return old_day

        return result[0][0]

    def __get_allowable_days_criteria(self, table_name: TableName) -> datetime.timedelta:
        if table_name.split('_')[-1] == 'annual':
            return datetime.timedelta(days=30 * 13)
        elif table_name.split('_')[-1] == 'quarter':
            return datetime.timedelta(days=30 * 7)
        elif table_name == TableName.MARKET_CAPITALIZATION:
            return datetime.timedelta(days=30 * 6)
        elif table_name == TableName.DAILY_PRICE:
            return datetime.timedelta(days=3)
        else:
            return datetime.timedelta(days=30 * 1)

    def __call_fmp_api_for_table(self, table_name: TableName, symbol=None, from_date=None):
        table_api: CallArgument = FMP_API[table_name]
        query_url_base = table_api.api_name

        url_combination = [query_url_base, ]
        if table_api.symbol_required:
            url_combination.append(symbol)
        api_url = "/".join(url_combination)
        if from_date and 'from' in table_api.default_param.keys():
            table_api.default_param['from'] = from_date

        return call_fmp_api(table_api.version, api_url, table_api.default_param)

    def __process_price_history_fmp_output(self, result: list[dict]) -> list[dict]:
        result_processed = []
        target_columns = ['date', 'adjClose', ]  # TODO constants
        for item in result['historical']:
            item_processed = {}
            try:
                [item_processed.update({k: item[k]}) for k in target_columns]
                result_processed.append(item_processed)
            except:  # NOTE price history contains item with weird size
                continue

        return result_processed

    def __get_update_stride_parameter(self, table_name: TableName) -> int:
        if table_name == TableName.MARKET_CAPITALIZATION:
            return 120
        if table_name == TableName.DAILY_PRICE:
            return 3

        return 1

    def download_and_update_raw_historical_table(self, table_name: TableName, ):
        session = scoped_session(self._session_maker)
        stride = self.__get_update_stride_parameter(table_name)

        symbol_list = self.get_all_symbol_list(session)
        tqdm_list = tqdm(symbol_list, leave=False)
        tqdm_list.set_description(f"{table_name}")

        update_status = {'total': len(symbol_list),
                         'already_latest': 0,
                         'no_data_from_fmp': 0,
                         'new_update_success': 0,
                         'sql_execute_failure': 0}

        for symbol in tqdm_list:
            latest_date = self.__get_latest_date_in_table(table_name, symbol, session)
            if (datetime.date.today() - latest_date) < self.__get_allowable_days_criteria(table_name):
                update_status['already_latest'] += 1
                continue

            result = self.__call_fmp_api_for_table(table_name=table_name, symbol=symbol, from_date=latest_date)
            if len(result) == 0:
                update_status['no_data_from_fmp'] += 1
                continue

            if result[0]['date'] == latest_date.strftime("%Y-%m-%d"):
                update_status['already_latest'] += 1  # FMP latest older than today
                continue

            if table_name == TableName.DAILY_PRICE:
                result = self.__process_price_history_fmp_output(result)

            result = result[::-1]
            [item.update({'symbol': symbol}) for item in result]
            all_column_types = self.__get_column_types(result[0])
            columns = (Column(k, v, primary_key=(k == 'symbol' or k == 'date'), index=(k == 'symbol' or k == 'date'))
                       for k, v in all_column_types.items())

            result = result[::stride]
            for i in range(0, len(result), BATCH_SIZE):
                if not self.__insert_table(table_name, result[i:i + BATCH_SIZE], columns, session):
                    update_status['sql_execute_failure'] += 1
                    continue

            update_status['new_update_success'] += 1

        print(f"{table_name} update_status: {update_status}")
        session.close()

    def update_resampled_historical_table(self, table_name: str):
        resample_period_list = {
            '1w': 7,
            '1m': 30,
            '3m': 90,
            '6m': 180,
            '1y': 365
        }
        session = scoped_session(self._session_maker)
        table_original = Table(table_name, self._meta)

        symbol_list = self.get_all_symbol_list(session)
        tqdm_list = tqdm(symbol_list, leave=False)
        tqdm_list.set_description(f"{table_name} resampling")

        for symbol in tqdm_list:

            df_result = self.__get_historical_table_on_symbol(table_name, symbol, session)
            if df_result is None:
                continue

            for resample_period, resample_days in resample_period_list.items():
                columns = (Column(column.name, column.type, primary_key=column.primary_key, index=column.index) for
                           column in table_original.c)
                table_name_resample = table_name + "_" + resample_period + core.constants.AVERAGE_TAG

                latest_date = self.__get_latest_date_in_table(table_name_resample, symbol, session)
                if datetime.date.today() - latest_date < datetime.timedelta(days=resample_days):
                    continue

                df_result_resampled = \
                    df_result.loc[df_result.index > latest_date.strftime("%Y-%m-%d")].resample(resample_period).mean()
                df_result_resampled.index = df_result_resampled.index.strftime("%Y-%m-%d")
                df_result_resampled.dropna(inplace=True)
                result_temp = df_result_resampled.reset_index().to_dict('records')
                result = [{'symbol': symbol, **item} for item in result_temp]
                for i in range(0, len(result), BATCH_SIZE):
                    if not self.__insert_table(table_name_resample, result[i:i + BATCH_SIZE], columns, session):
                        continue

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
                                       TableValue.Exchange.AMEX], limit=4000)

        table_list = [
            # TableName.INCOME_STATEMENT_ANNUAL, TableName.INCOME_STATEMENT_QUARTER,
            # TableName.FINANCIAL_RATIO_QUARTER, TableName.FINANCIAL_RATIO_ANNUAL,
            # TableName.CASHFLOW_ANNUAL, TableName.CASHFLOW_QUARTER,
            # TableName.BALANCE_SHEET_QUARTER, TableName.BALANCE_SHEET_ANNUAL,
            TableName.MARKET_CAPITALIZATION,
            # TableName.DAILY_PRICE,
        ]
        if len(table_list) > 0:
            with ThreadPoolExecutor(len(table_list)) as executor:
                executor.map(self.download_and_update_raw_historical_table, table_list)

        table_resample_list = [
            # TableName.DAILY_PRICE
        ]
        for table_resample in table_resample_list:
            self.update_resampled_historical_table(table_name=table_resample)

        table_pct_change_list = [
            TableName.MARKET_CAPITALIZATION,
            # TableName.FINANCIAL_RATIO_QUARTER, TableName.FINANCIAL_RATIO_ANNUAL,
            # TableName.DAILY_PRICE + ONE_WEEK_AVERAGE_TAG,
            # TableName.DAILY_PRICE + ONE_MONTH_AVERAGE_TAG,
            # TableName.DAILY_PRICE + THREE_MONTH_AVERAGE_TAG,
            # TableName.DAILY_PRICE + SIX_MONTH_AVERAGE_TAG,
        ]
        if len(table_pct_change_list) > 0:
            with ThreadPoolExecutor(len(table_pct_change_list)) as executor:
                executor.map(self.update_pct_change_historical_table, table_pct_change_list)

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

        result = session.execute(s).fetchall()
        df_table = pd.DataFrame(result)

        session.close()
        if df_table.empty:
            return None

        df_table.set_index('date', inplace=True)
        df_table.index = pd.DatetimeIndex(df_table.index)
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

    def past_average_filter(self, symbol_list: list[str], table_key: TableKey, from_date: datetime.date,
                            to_date: datetime.date, lower: float, upper: float, is_absolute=False, is_change=False) -> \
            list[str]:
        quoted_symbol_list = [f"'{symbol}'" for symbol in symbol_list]
        symbol_list_string = "(" + ", ".join(quoted_symbol_list) + ")"
        table_name: str = self.__find_table_name(table_key)
        if is_change:
            table_name += CHANGE_RATE_TAG
            if not self.__is_table_exist(table_name):
                print(f"No change rate table {table_name}. Cannot filter.")
                return []
        session = scoped_session(self._session_maker)

        if table_key.split('_')[-1] in PERIOD_TAG_LIST:
            table_key = "_".join(table_key.split('_')[0:-1])
        if table_key.split('_')[-1] in AVERAGE_TAG:
            table_key = "_".join(table_key.split('_')[0:-2])

        if is_absolute is False:
            sql_query = f"select symbol, average from " \
                        f"(select symbol, average, @counter := @counter + 1 as counter from" \
                        f"(select @counter:=0) as initVar, (select symbol, average FROM" \
                        f" (select symbol, AVG({table_key}) as average  FROM " \
                        f"{table_name} " \
                        f"where symbol in {symbol_list_string} and date < '{to_date}'  and date >'{from_date}' " \
                        f"GROUP BY symbol  order by average asc) " \
                        f" as orderedAverage where average is not null) as validOrderedAverage) as counteredvalidOrderedAverage " \
                        f"where counter <= {upper} * @counter and counter > {lower} * @counter ;"
        else:
            sql_query = f"SELECT * FROM (SELECT symbol, AVG({table_key}) as average FROM {table_name} " \
                        f"where date < '{to_date}'  and date >'{from_date}'  GROUP BY symbol) t where " \
                        f"t.average > {lower} and t.average < {upper}"

        result = session.execute(sql_query)
        session.close()

        df_result = pd.DataFrame(result)
        return list(df_result[TableKey.Profile.SYMBOL])

    def __get_historical_table_on_symbol(self, table_name: TableName, symbol: str, session=None) -> pd.DataFrame | None:

        sql_query = f"SELECT * FROM {str(table_name)} where symbol='{symbol}';"
        try:
            if session is not None:
                result_original = session.execute(sql_query).fetchall()
            else:
                result_original = self._conn.execute(sql_query).fetchall()

            df_result = pd.DataFrame(result_original)
            if df_result.empty:
                # print(f"While getting entire historical table {str(table_name)}: table does not have symbol {symbol}.")
                return None

            if 'date' not in df_result.columns:
                print(f"No date column. table {str(table_name)} is not a historical table.")
                return None

            df_result.replace(0, None)
            df_result.dropna(how="all", axis=0, thresh=2, inplace=True)  # thresh = 2 accounts symbol and date
            df_result.set_index('date', inplace=True)
            df_result.index = pd.DatetimeIndex(df_result.index)

        except Exception as e:
            print({e})
            print(f"sql execution failed.")
            return None
        return df_result

    def __post_process_historical_dataframe(self, df_result: pd.DataFrame):
        df_result.replace(0, None, inplace=True)
        df_result.dropna(how="all", axis=0, thresh=2, inplace=True)  # thresh = 2 accounts symbol and date
        return df_result

    def update_pct_change_historical_table(self, table_name: TableName):
        session = scoped_session(self._session_maker)
        new_table_name = table_name + CHANGE_RATE_TAG

        symbol_list = self.get_all_symbol_list(session)
        tqdm_list = tqdm(symbol_list, leave=False)
        tqdm_list.set_description(f"{table_name} pct_change")

        update_status = {'total': len(symbol_list),
                         'no_history': 0,
                         'only_single_history': 0,
                         'no_valid_row_after_processing': 0,
                         'new_update_success': 0,
                         'sql_execute_failure': 0}

        for symbol in tqdm_list:
            latest_date = self.__get_latest_date_in_table(new_table_name, symbol, session)
            if (datetime.date.today() - latest_date) < self.__get_allowable_days_criteria(table_name):
                continue

            df_result = self.__get_historical_table_on_symbol(table_name, symbol, session)

            if df_result is None:
                update_status['no_history'] += 1
                continue
            if len(df_result) == 1:
                update_status['only_single_history'] += 1
                continue
            df_result = self.__post_process_historical_dataframe(df_result)
            if df_result.empty:
                update_status['no_valid_row_after_processing'] += 1
                continue

            numeric_columns = [column for column in df_result.columns if
                               is_numeric_dtype(df_result[column])]

            df_change_symbol = pd.concat(
                [df_result['symbol']] +
                [df_result[numeric_column].pct_change() for numeric_column in
                 numeric_columns], axis=1)
            df_change_symbol = df_change_symbol.iloc[1:]  # first row of pct_change is None
            df_change_symbol.index = df_change_symbol.index.strftime("%Y-%m-%d")

            result = df_change_symbol.reset_index().to_dict('records')
            all_column_types = self.__get_column_types(result[0])
            columns = (Column(k, v, primary_key=(k == 'symbol' or k == 'date'), index=(k == 'symbol' or k == 'date'))
                       for k, v in all_column_types.items())

            for i in range(0, len(result), BATCH_SIZE):
                if not self.__insert_table(new_table_name, result[i:i + BATCH_SIZE], columns, session):
                    update_status['sql_execute_failure'] += 1
                    continue
            update_status['new_update_success'] += 1

        print(f"{table_name} pct_change update_status: {update_status}")
        session.close()


if __name__ == "__main__":
    start_time = time.time()
    db_interface = DataBaseInterface()
    db_interface.update(renew_profile_table=False)
    elapsed = (time.time() - start_time)
    print(f"\nElapsed: {elapsed} sec")
