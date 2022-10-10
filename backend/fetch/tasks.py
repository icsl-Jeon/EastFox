from background_task import background
from dotenv import load_dotenv

from urllib.request import urlopen
import json
import ssl
import os

API_KEY = os.environ.get("apikey")
SOURCE_DOMAIN = "https://financialmodelingprep.com"

from .models import *


def get_jsonparsed_data(url):
    try:
        ssl_context = ssl.create_default_context()
        response = urlopen(url, context=ssl_context)
        data = response.read().decode("utf-8")
        return json.loads(data)
    except Exception as e:
        print(f"While getting {url}, occurred: {e}")
        return {}


def get_all_symbols_from_source() -> list[str]:
    url = "f{SOURCE_DOMAIN}/api/v3/available-traded/list?apikey={API_KEY}"
    return get_jsonparsed_data(url)


def get_symbol_detail_from_source(symbol: str) -> dict:
    url = f"{SOURCE_DOMAIN}/api/v3/profile/{symbol}?apikey={API_KEY}"
    return get_jsonparsed_data(url)


def get_asset_model_from_detail(detail_from_source: dict) -> Asset:
    asset_type_string = "STOCK"
    if detail_from_source['isEtf']:
        asset_type_string = "ETF"
    if detail_from_source['isFund']:
        asset_type_string = "FUND"

    asset_type = AssetType(asset_type_string)
    # TODO: create Asset model from fmpsdk
