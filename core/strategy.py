import datetime
from enum import Enum
from dataclasses import dataclass
import pandas as pd
from typing import Union
from fetch import Fetcher


class SelectorType(Enum):
    PROFILE = 0
    POINT_VALUE = 1
    HORIZON_RANGE = 2


@dataclass
class Selector:
    type: SelectorType
    key: str
    value: Union[str, tuple[float, float]]
    horizon: int
    is_absolute: bool


@dataclass
class SelectorSequence:
    selectors: list[Selector]


@dataclass
class Filter:
    name: str
    selector_sequence_union: list[SelectorSequence]


@dataclass
class Asset:
    symbol: str

    def __eq__(self, other):
        return self.symbol == other.symbol

    def __hash__(self):
        return hash(self.symbol)


@dataclass
class Segment:
    start_date: datetime.date
    end_date: datetime.date
    assets: list[Asset]

    def get_asset_symbol_list(self):
        return [asset.symbol for asset in self.assets]


class Strategist:
    def __init__(self, name: str, fetcher: Fetcher,
                 asset_pool: list[Asset],
                 start_date: datetime.date, end_date: datetime.date) -> None:
        initial_segment = Segment(
            start_date=start_date, end_date=end_date, assets=asset_pool)
        self.name = name
        self.fetcher = fetcher
        self.state = [initial_segment]
        self.asset_pool = asset_pool
        pass

    def __apply_selector_sequence(self, selector_sequence: SelectorSequence, query_date: datetime.date) -> set[Asset]:
        asset_pool = self.asset_pool.copy()
        for selector in selector_sequence.selectors:

            table_dict = self.fetcher._table_dict
            horizon_end = query_date.strftime('%Y-%m-%d')
            horizon_start = (query_date - datetime.timedelta(days=365 * selector.horizon)).strftime('%Y-%m-%d')

            symbol_list = [asset.symbol for asset in asset_pool]
            mean_table_asset_pool: pd.Series = \
                table_dict[selector.key][horizon_start:horizon_end][symbol_list].mean()

            if not selector.is_absolute:
                mean_table_asset_pool = mean_table_asset_pool.rank(pct=True)

            selected_assets = mean_table_asset_pool[
                mean_table_asset_pool.between(selector.value[0], selector.value[1])].index.tolist()
            selected_assets.sort()

            # TODO relative handling by .rank(pct=True)
            if isinstance(selector.value, tuple):
                asset_pool = [Asset(symbol=symbol) for symbol in selected_assets]
            else:
                pass
        return set(asset_pool)

    def select_assets(self, filter: Filter, rebalance_date: datetime.date):
        belong_idx = -1
        for idx, segment in enumerate(self.state):
            if (segment.start_date <= rebalance_date) & (rebalance_date <= segment.end_date):
                belong_idx = idx
                break
        if belong_idx < 0:
            print('filter time location is not valid')
            return

        filtered_assets = set()
        for selector_sequence in filter.selector_sequence_union:
            assets_from_selector_sequence \
                = self.__apply_selector_sequence(selector_sequence, rebalance_date)
            filtered_assets = filtered_assets.union(assets_from_selector_sequence)

        asset_list_sorted = [asset.symbol for asset in list(filtered_assets)]
        asset_list_sorted.sort()
        filtered_assets = [Asset(symbol=symbol) for symbol in asset_list_sorted]
        shrink_segment = self.state[belong_idx]
        inserted_segment = Segment(start_date=rebalance_date, end_date=shrink_segment.end_date,
                                   assets=list(filtered_assets))
        shrink_segment.end_date = rebalance_date
        self.state[belong_idx] = shrink_segment
        self.state.insert(belong_idx + 1, inserted_segment)
