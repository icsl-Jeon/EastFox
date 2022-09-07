import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy import inspect, types
from sqlalchemy.dialects.mysql import insert

from urllib.request import urlopen
import certifi
import json
from aenum import StrEnum, skip, auto

import pandas as pd
from core.constants import TableKey, TableValue, get_all_sub_tables

load_dotenv()
DB_USERNAME = os.environ.get("sql_user")
DB_PASSWORD = os.environ.get("sql_password")
DB_NAME = os.environ.get("sql_db_name")
DB_IP = os.environ.get("sql_ip")
DB_PORT = os.environ.get("sql_port")
API_KEY = os.environ.get("apikey")


def get_jsonparsed_data(url):
    response = urlopen(url, cafile=certifi.where())
    data = response.read().decode("utf-8")
    return json.loads(data)


class TableName(StrEnum):
    PROFILE = "profile"


class DataBaseInterface:

    def __init__(self):
        db_url = f"mariadb+mariadbconnector://{DB_USERNAME}:{DB_PASSWORD}@{DB_IP}:{DB_PORT}/"f"{DB_NAME}"
        self._engine = create_engine(db_url, pool_pre_ping=True, pool_recycle=3600)
        self._conn = self._engine.connect()
        self._table_dict = dict()
        self._meta = MetaData()
        self._meta.reflect(self._conn)
        self._inspector = inspect(self._engine)

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

    def __insert_table(self, table_name: str, values: list[dict], columns) -> bool:
        table = Table(table_name, self._meta, *columns,
                      extend_existing=True)

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

    def update_profile_table(self, target_exchange_list=list[TableValue.Exchange]) -> bool:
        table_name = TableName.PROFILE
        is_this_first_create = not self.__is_table_exist(TableName.PROFILE)

        url = f"https://financialmodelingprep.com/api/v3/stock/list?apikey={API_KEY}"
        result: list[dict] = get_jsonparsed_data(url)
        if len(result) == 0:
            return False

        all_column_types = self.__get_column_types(result[0])
        target_key_list = [item for item in get_all_sub_tables(TableKey.Profile) if
                           item in list(all_column_types.keys())]

        target_column_types = (Column(TableKey.Profile.SYMBOL, types.VARCHAR(20), primary_key=True),
                               Column(TableKey.Profile.NAME, types.TEXT()),
                               Column(TableKey.Profile.SECTOR, types.VARCHAR(200)),
                               Column(TableKey.Profile.INDUSTRY, types.TEXT()),
                               Column(TableKey.Profile.EXCHANGE, types.VARCHAR(20)),
                               Column(TableKey.Profile.TYPE, types.VARCHAR(20)))

        for item in result:
            if item[TableKey.EXCHANGE] not in target_exchange_list:
                continue
            url = f"https://financialmodelingprep.com/api/v3/profile/{item[TableKey.Profile.SYMBOL]}?apikey={API_KEY}"
            profile_result = get_jsonparsed_data(url)
            target_item = {k: item[k] for k in target_key_list}
            target_item.update(
                {str(k): profile_result[0][k] for k in [TableKey.Profile.INDUSTRY, TableKey.Profile.SECTOR]})

            if not self.__insert_table(table_name, [target_item], target_column_types):
                continue

        if is_this_first_create:
            return self.__set_primary_key(table_name, TableKey.Profile.SYMBOL)


if __name__ == "__main__":
    db_interface = DataBaseInterface()
    db_interface.update_profile_table([TableValue.Exchange.NYSE,
                                       TableValue.Exchange.NASDAQ,
                                       TableValue.Exchange.AMEX])
    pass
