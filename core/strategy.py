import datetime
from enum import Enum
from dataclasses import dataclass
import pandas as pd


class SelectorType(Enum):
    PROFILE = 0
    POINT_VALUE = 1
    HORIZON_RANGE = 2


@dataclass
class Selector:
    type: SelectorType
    key: str


@dataclass
class SelectorSequence:
    selectors: list[Selector]


@dataclass
class Filter:
    selector_sequence_union: list[SelectorSequence]


@dataclass
class Holding:
    symbol: str


@dataclass
class Segment:
    start_date: datetime.date
    end_date: datetime.date
    holdings: list[Holding]


class Strategist:
    def __init__(self, database_list: list[pd.DataFrame],
                 initial_holdings: list[Holding],
                 start_date: datetime.date, end_date: datetime.date) -> None:
        initial_segment = Segment(
            start_date=start_date, end_date=end_date, holdings=initial_holdings)
        self.database_list = database_list
        self.state = [initial_segment]
        pass

    def apply_filter(self, filter: Filter, date: datetime.date):
        belong_idx = -1
        for idx, segment in enumerate(self.state):
            if (segment.start_date <= date) & (date <= segment.end_date):
                belong_idx = idx
                break
        if (belong_idx < 0):
            print('filter time location is not valid')
            return

        shrinked_segment = self.state[belong_idx]
        inserted_segment = Segment(start_date=date, end_date=shrinked_segment.end_date, holdings=[])
        shrinked_segment.end_date = date
        self.state[belong_idx] = shrinked_segment
        self.state.insert(belong_idx, inserted_segment)
