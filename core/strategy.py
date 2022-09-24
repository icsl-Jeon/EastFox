import datetime
from datetime import timedelta
from enum import Enum
from dataclasses import dataclass
import pandas as pd
from typing import Union
from core.db_interface import DataBaseInterface
from core.constants import TableKey


class SelectorType(Enum):
    PROFILE = 0
    POINT_VALUE = 1
    HORIZON_RANGE = 2
    INCLUSION = 4
    GROWTH = 5  # TODO


@dataclass
class Selector:
    type: SelectorType
    key: TableKey
    value: Union[list[str], tuple[float, float]]
    horizon: int = 1
    is_absolute: bool = True


@dataclass
class SelectorSequence:
    selectors: list[Selector]


@dataclass
class Filter:
    name: str
    selector_sequence_union: list[SelectorSequence]


@dataclass
class Segment:
    start_date: datetime.date
    end_date: datetime.date
    assets: list[str]


class Strategist:
    def __init__(self, name: str, fetcher: DataBaseInterface,
                 asset_pool: list[str],
                 start_date: datetime.date, end_date: datetime.date) -> None:
        self.name = name
        self.state = [Segment(start_date=start_date, end_date=end_date, assets=asset_pool)]

        self._asset_pool = asset_pool
        self._fetcher = fetcher

    def __apply_selector_sequence(self, selector_sequence: SelectorSequence, query_date: datetime.date) -> set[str]:
        asset_pool = self._asset_pool.copy()
        for selector in selector_sequence.selectors:

            if selector.type == SelectorType.PROFILE:
                df_profile: pd.DataFrame = self._fetcher.get_profile_list(selector.key, asset_pool)
                df_profile_selected: pd.DataFrame = df_profile.loc[df_profile[selector.key].isin(selector.value)]
                asset_pool = (df_profile_selected[TableKey.Profile.SYMBOL]).tolist()

            elif selector.type == SelectorType.HORIZON_RANGE:
                asset_pool = self._fetcher.past_average_filter(symbol_list=asset_pool, table_key=selector.key,
                                                               from_date=query_date - timedelta(365 * selector.horizon),
                                                               to_date=query_date, is_absolute=selector.is_absolute,
                                                               lower=selector.value[0], upper=selector.value[1])
            elif selector.type == SelectorType.GROWTH:
                asset_pool = self._fetcher.past_average_filter(symbol_list=asset_pool, table_key=selector.key,
                                                               from_date=query_date - timedelta(365 * selector.horizon),
                                                               to_date=query_date, is_absolute=selector.is_absolute,
                                                               lower=selector.value[0], upper=selector.value[1],
                                                               is_change=True)
                pass
            else:
                asset_pool = []
                pass

            asset_pool.sort()
        return set(asset_pool)

    def __find_segment_index(self, query_date: datetime.date) -> int:
        belong_idx = -1
        for idx, segment in enumerate(self.state):
            if (segment.start_date <= query_date) & (query_date <= segment.end_date):
                belong_idx = idx
                break
        return belong_idx

    def apply_filter(self, filter_in: Filter, date_in: datetime.date):
        applied_segment_index = self.__find_segment_index(date_in)
        if applied_segment_index < 0:
            print(f'None of segment include date {date_in}')
            return

        filtered_symbols = set()
        for selector_sequence in filter_in.selector_sequence_union:
            assets_from_selector_sequence \
                = self.__apply_selector_sequence(selector_sequence, date_in)
            filtered_symbols = filtered_symbols.union(assets_from_selector_sequence)
        filtered_symbols = list(filtered_symbols)

        if not len(filtered_symbols):
            print(f"Filtering failed. skipping {date_in}")
            return
        filtered_symbols.sort()

        shrink_segment = self.state[applied_segment_index]
        inserted_segment = Segment(start_date=date_in, end_date=shrink_segment.end_date, assets=filtered_symbols)
        shrink_segment.end_date = date_in

        self.state[applied_segment_index] = shrink_segment
        self.state.insert(applied_segment_index + 1, inserted_segment)

    def show_asset_selection(self):
        asset_selected = []
        from collections import Counter

        for segment in self.state:
            asset_selected += segment.assets

        asset_counts = Counter(asset_selected)
        sorted_counts = pd.Series(asset_counts, name="select count").sort_index()
        sorted_counts = sorted_counts[sorted_counts > 1]

        return sorted_counts
