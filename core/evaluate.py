from core.strategy import Strategist, Segment
from core.db_interface import DataBaseInterface
from core.constants import *
import matplotlib.pyplot as plt
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


def show_selection(strategist: Strategist, fetcher: DataBaseInterface, draw_props=dict()):
    fontsize = 10
    radius = 2
    palette = "cubehelix"
    labeldistacne = 1.2

    if 'fontsize' in draw_props:
        fontsize = draw_props['fontsize']
    if 'radius' in draw_props:
        radius = draw_props['radius']
    if 'palette' in draw_props:
        palette = draw_props['palette']
    if 'labeldistacne' in draw_props:
        labeldistacne = draw_props['labeldistacne']

    sector_counter = extract_sector_count_from_segment(strategist.state[1], fetcher)
    for segment in strategist.state[2:]:
        sector_counter += extract_sector_count_from_segment(segment, fetcher)

    sector_counter.sort_values()
    color_mapper = generate_sector_color(list(sector_counter.index), palette)
    color_pie = [color_mapper[sector_name] for sector_name in list(sector_counter.index)]
    sector_counter.plot.pie(colors=color_pie, radius=radius, labeldistance=labeldistacne)
    plt.gca().set_title(strategist.name, fontsize=fontsize)
    plt.gca().get_yaxis().set_visible(False)
