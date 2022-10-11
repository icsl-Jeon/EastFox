import datetime

from background_task import background
from dotenv import load_dotenv

from urllib.request import urlopen
import json
import ssl
import os

load_dotenv()
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


def fetch_all_symbols() -> list[str]:
    url = f"{SOURCE_DOMAIN}/api/v3/available-traded/list?apikey={API_KEY}"
    return [item['symbol'] for item in get_jsonparsed_data(url)]


def fetch_profile_with_symbol(symbol: str) -> dict:
    url = f"{SOURCE_DOMAIN}/api/v3/profile/{symbol}?apikey={API_KEY}"
    try:
        return get_jsonparsed_data(url)[0]
    except Exception as e:
        print(f"While getting {url}, occurred: {e}")
        return {}


def create_asset_model(profile_from_source: dict) -> Asset:
    symbol = profile_from_source['symbol']
    exchange = Exchange(profile_from_source['exchangeShortName'])
    sector = Sector(profile_from_source['sector'])

    asset_type_string = "STOCK"
    if profile_from_source['isEtf']:
        asset_type_string = "ETF"
        sector = None
    if profile_from_source['isFund']:
        asset_type_string = "FUND"

    asset_type = AssetType(asset_type_string)
    # TODO: create Asset model from fmpsdk

    name = profile_from_source['companyName']
    industry = profile_from_source['industry']
    ipo_date = profile_from_source['ipoDate']

    return Asset(symbol=symbol,
                 exchange=exchange,
                 sector=sector,
                 type=asset_type,
                 name=name,
                 industry=industry,
                 ipo_date=ipo_date)


@background(schedule=1)
def update_asset_database():
    symbols = fetch_all_symbols()
    print(f"{datetime.datetime.now()}: Fetched {len(symbols)} symbols from source.")
    n_total_symbols = len(symbols)
    n_newly_updated_symbols = 0

    for count, symbol in enumerate(symbols):
        if count % 100 == 0 and count > 0:
            print(f"[{count}/{n_total_symbols}] {n_newly_updated_symbols} symbols were newly updated..")

        if Asset.objects.filter(symbol=symbol).count():
            continue

        profile = fetch_profile_with_symbol(symbol)
        if len(profile) == 0:
            continue

        asset = create_asset_model(profile)
        try:
            asset.save()
        except Exception as e:
            print(f"Skipping DB update for {symbol} due to: {e}")
            continue

        n_newly_updated_symbols += 1
