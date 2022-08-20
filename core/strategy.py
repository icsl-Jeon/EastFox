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


@dataclass
class SelectorSequence:
    selectors: list[Selector]


@dataclass
class Filter:
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


class Strategist:
    def __init__(self, fetcher: Fetcher,
                 asset_pool: list[Asset],
                 start_date: datetime.date, end_date: datetime.date) -> None:
        initial_segment = Segment(
            start_date=start_date, end_date=end_date, assets=asset_pool)
        self.fetcher = fetcher
        self.state = [initial_segment]
        self.asset_pool = asset_pool
        pass

    def __apply_selector_sequence(self, selector_sequence: SelectorSequence, query_date: datetime.date) -> list[Asset]:
        asset_pool = self.asset_pool.copy()
        for selector in selector_sequence.selectors:
            asset_pool_value = pd.Series(index=[holding.symbol for holding in asset_pool], dtype=float)

            history_reverse_search_start = None
            for asset in asset_pool:
                if selector.type == SelectorType.HORIZON_RANGE:
                    value_past_horizon, history_reverse_search_start = \
                        self.fetcher.fetch_past(key=selector.key,
                                                symbol=asset.symbol,
                                                query_date=query_date,
                                                horizon=selector.horizon,
                                                reverse_search_idx_hint=history_reverse_search_start)
                    asset_pool_value[asset.symbol] = value_past_horizon.values.mean()
                else:
                    pass

            # TODO relative handling by .rank(pct=True)
            if isinstance(selector.value, tuple):
                asset_pool = [Asset(symbol=symbol) for symbol in asset_pool_value[
                    asset_pool_value.between(selector.value[0], selector.value[1])].index.tolist()]
            else:
                pass
        return asset_pool

    def select_assets(self, filter: Filter, rebalance_date: datetime.date):
        belong_idx = -1
        for idx, segment in enumerate(self.state):
            if (segment.start_date <= rebalance_date) & (rebalance_date <= segment.end_date):
                belong_idx = idx
                break
        if (belong_idx < 0):
            print('filter time location is not valid')
            return

        for filter

        shrink_segment = self.state[belong_idx]
        inserted_segment = Segment(start_date=rebalance_date, end_date=shrink_segment.end_date, assets=[])
        shrink_segment.end_date = rebalance_date
        self.state[belong_idx] = shrink_segment
        self.state.insert(belong_idx + 1, inserted_segment)
