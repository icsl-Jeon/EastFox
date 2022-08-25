import datetime
from dataclasses import dataclass
from strategy import Strategist
import pandas as pd
from strategy import Segment
from fetch import *
import matplotlib.pyplot as plt

DAILY_KEY = 'daily'
WEEKLY_KEY = 'weekly'
MONTHLY_KEY = 'monthly'
YEARLY_KEY = 'yearly'
PRICE_KEY = 'price_list'
PRICE_PCT_CHANGE_DAILY_KEY = DAILY_KEY + '_change'
PRICE_PCT_CHANGE_MONTHLY_KEY = MONTHLY_KEY + '_change'
PRICE_PCT_CHANGE_YEARLY_KEY = YEARLY_KEY + '_change'

color_set = ['b', 'g', 'c', 'r', 'm']


@dataclass
class ReportRecipe:
    resolution: str
    start_date: datetime.date
    end_date: datetime.date
    pass


@dataclass
class StrategyReport:
    name: str
    color: str
    account_history: pd.Series
    segment_list: list[Segment]
    property_dict: dict
    pass


class Analyst:
    def __init__(self, fetcher: Fetcher):
        self.table_dict = dict()
        self.strategy_report_list = list()
        self.fetcher = fetcher

    def register(self, table_name: str, csv_file_directory: str):
        try:
            df_file = pd.read_csv(csv_file_directory)
            if isinstance(df_file.index, pd.RangeIndex):
                if df_file.columns.tolist().count('date') == 0:
                    print('Columns should include "date" when indexing was not applied in csv !')
                    return
                df_file.set_index('date', inplace=True)
                df_file.index = pd.to_datetime(df_file.index)
                df_file.sort_index(inplace=True)
            elif isinstance(df_file.index, pd.DatetimeIndex):
                pass
            else:
                print('Table should have either date column or date index !')
                return

        except:
            print('Could not read {}'.format(csv_file_directory))
            return

        resample_period_list = {WEEKLY_KEY: '1W', MONTHLY_KEY: '1M', YEARLY_KEY: '1Y'}
        resample_period_key_list = [DAILY_KEY, WEEKLY_KEY, MONTHLY_KEY, YEARLY_KEY]

        table_periods = dict.fromkeys(resample_period_key_list)
        table_periods[DAILY_KEY] = df_file.copy()
        for period in resample_period_key_list[1:]:
            table_periods[period] = df_file.resample(resample_period_list[period]).last()

        self.table_dict.update({table_name: table_periods})

    def attach(self, strategist: Strategist):
        if strategist.state is None:
            return
        if not (PRICE_KEY in self.table_dict.keys()):
            return

        total_initial = 1
        total_history = pd.Series(dtype=float)

        for segment in strategist.state:
            segment_start_date = segment.start_date.strftime('%Y-%m-%d')
            segment_end_date = segment.end_date.strftime('%Y-%m-%d')
            symbols = segment.get_asset_symbol_list()
            table_key = DAILY_KEY
            df_price_table = self.table_dict[PRICE_KEY][table_key]
            df_segment_price_history = df_price_table[segment_start_date:segment_end_date][symbols]
            df_segment_price_history.dropna(axis=1, inplace=True)
            initial_price_list = df_segment_price_history.iloc[0]
            holding_list = initial_price_list.apply(lambda x: total_initial / x / len(initial_price_list))
            segment_series = df_segment_price_history.apply(lambda x: x.dot(holding_list), axis=1)
            total_history = pd.concat([total_history, segment_series[:-1]])
            total_initial = segment_series[-1]

        report = StrategyReport(name=strategist.name, account_history=total_history, segment_list=strategist.state,
                                property_dict={}, color=color_set[len(self.strategy_report_list)])

        report.property_dict.update({})


        self.strategy_report_list.append(report)

    def update_assets_property(self, property_key: str):
        for report in self.strategy_report_list:
            property_values_history = dict()
            for segment in report.segment_list:
                symbol_list = segment.get_asset_symbol_list()
                segment_start_date = segment.start_date.strftime('%Y-%m-%d')
                segment_end_date = segment.end_date.strftime('%Y-%m-%d')
                property_mean_list = self.fetcher.query(key=property_key, slice_start_date=segment_start_date,
                                                        slice_end_date=segment_end_date, symbols=symbol_list).mean()
                property_values_history.update({segment.start_date: property_mean_list})
            report.property_dict.update({property_key: property_values_history})

    def get_report(self, name: str, report_recipe: ReportRecipe) -> StrategyReport:
        pass

    def draw_price_history(self):
        for report in self.strategy_report_list:
            plt.plot(report.account_history, report.color, label=report.name, )
        plt.legend()

    def draw_property_distributions(self):

        report_list = self.strategy_report_list
        if not report_list:
            return
        registered_property_list = list(report_list[0].property_dict.keys())
        n_property = len(registered_property_list)
        for n in range(n_property):
            plt.subplot(n_property, 1, n + 1)

            property_key = registered_property_list[n]
            plt.gca().set_title(property_key)

            property_distribution_list = []
            for report in self.strategy_report_list:
                property_distribution = []
                property_value_series_list = list(report.property_dict[property_key].values())
                for property_value_series in property_value_series_list:
                    property_value_series.dropna(inplace=True)
                    property_distribution += property_value_series.values.tolist()
                property_distribution_list.append(property_distribution)

            box_plot = plt.boxplot(property_distribution_list,
                                   showfliers=False,
                                   notch=True, patch_artist=True, widths=0.6);

            for box, report in zip(box_plot['boxes'], self.strategy_report_list):
                box.set_facecolor(report.color)

        pass
