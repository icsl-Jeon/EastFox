from core.strategy import Strategist, Segment
from core.db_interface import DataBaseInterface
from core.constants import *
import matplotlib.pyplot as plt
import datetime
import matplotlib.dates as mdates
from collections import Counter
import pandas as pd
import seaborn as sns


def generate_sector_color(sector_list: list[str], palette: str):
    sector_list.sort()
    colors = sns.color_palette(palette, len(sector_list))
    return {k: v for k, v in zip(sector_list, colors)}


SECTOR_COLOR_MAP = {'Basic Materials': (0.0949778838058352, 0.06254211781552795, 0.15417987083084048),
                    'Communication Services': (0.09641540616370546, 0.17728671859553138, 0.28347363185399654),
                    'Services': (0.09641540616370546, 0.17728671859553138, 0.28347363185399654),
                    'Consumer Cyclical': (0.08523511613408935, 0.32661779003565533, 0.2973201282529313),
                    'Consumer Defensive': (0.17004232121057958, 0.43679759647517286, 0.22372555555555548),
                    'Energy': (0.37510867095095474, 0.47935988952053404, 0.18482861741555928),
                    'Financial Services': (0.6328422475018423, 0.4747981096220677, 0.29070209208025455),
                    'Healthcare': (0.7984646490425262, 0.48658654436309784, 0.5244405422521965),
                    'Industrials': (0.8299576787894204, 0.5632024035248271, 0.7762744444444445),
                    'Real Estate': (0.7779565181455343, 0.7069421942599752, 0.9314406084043191),
                    'Technology': (0.7632674462838152, 0.850242277575182, 0.9515539762051686),
                    'Utilities': (0.8510181086946101, 0.9480529957653149, 0.9362754507718345)}


def extract_sector_count_from_segment(segment: Segment, fetcher: DataBaseInterface):
    assets_in_state = segment.assets
    profile_in_state = fetcher.get_profile_table(assets_in_state)
    sector_count = \
        profile_in_state.groupby([TableKey.Profile.SECTOR]).count()[TableKey.Profile.SYMBOL]
    sector_count = sector_count[sector_count > 1]
    sector_count /= sector_count.sum()
    sector_count *= 100
    sector_count.sort_index()
    return sector_count


def draw_sector_distribution_history_bar(position, segment: Segment, fetcher: DataBaseInterface):
    sector_counts = extract_sector_count_from_segment(segment, fetcher)
    bottom = 0
    for index, sector in sector_counts.items():
        color = SECTOR_COLOR_MAP[index]
        height = sector
        plt.bar(position, height, bottom=bottom, color=color)
        bottom += height


def show_selection(strategist: Strategist, fetcher: DataBaseInterface, **kwargs):
    fontsize = kwargs.get("fontsize", 10)
    radius = kwargs.get("radius", 2)
    palette = kwargs.get("palette", "cubehelix")
    labeldistacne = kwargs.get("labeldistacne", 1.2)

    sector_counter = extract_sector_count_from_segment(strategist.state[1], fetcher)
    for segment in strategist.state[2:]:
        sector_counter += extract_sector_count_from_segment(segment, fetcher)

    sector_counter.sort_values()
    color_pie = [SECTOR_COLOR_MAP[sector_name] for sector_name in list(sector_counter.index)]
    sector_counter.plot.pie(colors=color_pie, radius=radius, labeldistance=labeldistacne)
    plt.gca().set_title(strategist.name, fontsize=fontsize)
    plt.gca().get_yaxis().set_visible(False)


def get_all_symbols(strategist: Strategist, include_first_segment=False) -> list[str]:
    symbols = set()
    for segment in strategist.state[int(not include_first_segment):]:
        symbols = symbols.union(set(segment.assets))
    return list(symbols)


def get_all_symbols_price_history(strategist: Strategist, fetcher: DataBaseInterface, include_initial_segment=False):
    strategist_start_date = strategist.state[0].start_date
    strategist_end_date = strategist.state[-1].end_date

    total_symbols = get_all_symbols(strategist, include_initial_segment)
    df_all_price_history = fetcher.get_history_list(table_key=TableKey.PRICE_HISTORY, symbol_list=total_symbols,
                                                    from_date=strategist_start_date, to_date=strategist_end_date)
    print(f"{len(df_all_price_history.columns)} / {len(total_symbols)} 종목이 유효한 가격히스토리를 가지고 있습니다.")
    return df_all_price_history


def estimate_price_history(strategist: Strategist, fetcher: DataBaseInterface | pd.DataFrame, **kwargs) -> pd.Series:
    resample_days = kwargs.get("resample_days", '6D')
    non_nan_ratio_for_valid_column = kwargs.get("non_nan_ratio_for_valid_column", 0.8)
    include_initial_segment = kwargs.get("include_initial_segment", False)

    if isinstance(fetcher, DataBaseInterface):
        df_all_price_history = get_all_symbols_price_history(strategist, fetcher)
    else:
        df_all_price_history = fetcher

    total_history = pd.Series(dtype=float, name=strategist.name)
    total_initial = 1
    for segment in strategist.state[int(not include_initial_segment):]:
        symbols = segment.assets
        symbols_with_price = [symbol for symbol in symbols if symbol in df_all_price_history.columns]
        df_segment_price_history = df_all_price_history[segment.start_date:segment.end_date][symbols_with_price]
        df_segment_price_history = df_segment_price_history.resample(resample_days).mean()

        # TODO handle exceptional cases
        df_segment_price_history.dropna(inplace=True, axis=1,
                                        thresh=int(len(df_segment_price_history) * non_nan_ratio_for_valid_column))
        df_segment_price_history.fillna(method='ffill', inplace=True)
        df_segment_price_history.fillna(method='bfill', inplace=True)
        is_all_rows_greater_than_zero = df_segment_price_history.gt(0).all(axis=0)
        df_segment_price_history = df_segment_price_history[
            is_all_rows_greater_than_zero[is_all_rows_greater_than_zero].index]

        if len(df_segment_price_history.columns) < len(symbols) * 0.5:
            print(
                f"Too small number of stocks {len(df_segment_price_history.columns)} survived."
                f" (less than half of symbols of segment)")
        initial_price_list = df_segment_price_history.iloc[0]
        holding_list = initial_price_list.apply(lambda x: total_initial / x / len(initial_price_list))
        segment_series = df_segment_price_history.apply(lambda x: x.dot(holding_list), axis=1)
        total_history = pd.concat([total_history, segment_series[:-1]])
        total_initial = segment_series[-1]
        if total_initial != total_initial:
            print("Encountered nan value during history calculation. Stopping estimation")
            total_history = total_history[0:total_history.last_valid_index()]
            return total_history

    return total_history


def analyze_impact(strategist: Strategist, fetcher: DataBaseInterface, ) -> tuple[pd.Series, pd.DataFrame]:
    df_all_price_history = get_all_symbols_price_history(strategist, fetcher)
    df_all_price_history_resample = df_all_price_history.resample('6D').mean()  # TODO param

    averaged_accumulation = pd.Series(index=df_all_price_history_resample.columns, dtype=float)
    for column in df_all_price_history_resample:
        column_series = df_all_price_history_resample[column]
        valid_horizon_start = column_series.first_valid_index()
        valid_horizon_end = column_series.last_valid_index()
        initial_value = column_series[valid_horizon_end]
        column_series /= initial_value
        if (valid_horizon_end - valid_horizon_start).days > 1:
            integration = column_series.sum() / (valid_horizon_end - valid_horizon_start).days
            averaged_accumulation[column] = integration

    return averaged_accumulation, df_all_price_history_resample


def prepare_canvas(**kwargs):
    plt.subplots(constrained_layout=True, figsize=(10, 10))
    plt.rcParams['figure.dpi'] = kwargs.get("dpi", 150)  # default for me was 75
    plt.rcParams.update({'font.size': kwargs.get("fontsize", 14)})
    plt.rcParams['font.family'] = kwargs.get("fontfamily", 'Malgun Gothic')
    plt.rcParams['axes.unicode_minus'] = False
