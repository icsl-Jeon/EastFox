import datetime
from dataclasses import dataclass
from strategy import Strategist
import pandas as pd
from strategy import Segment
from fetch import *
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

DAILY_KEY = 'daily'
WEEKLY_KEY = 'weekly'
MONTHLY_KEY = 'monthly'
YEARLY_KEY = 'yearly'


class TableNameList:
    STOCK_PRICE = 'price_list'
    ECONOMIC_INDICATOR = 'economic_indicator'
    MARKET_INDEX = 'market_index'
    ETC = 'misc'


class MarketIndexList:
    SNP500 = '^GSPC'
    TREASURY_5YEAR = '^FVX'
    TREASURY_10YEAR = '^TNX'
    TREASURY_30YEAR = '^TYX'


class EconomicIndicatorList:
    CPI = 'CPI'
    INFLATION_RATE = 'inflationRate'
    INFLATION = 'inflation'
    UNEMPLOYMENT_RATE = 'unemploymentRate'


class EtcList:
    BITCOIN = 'BTCUSD'
    COVID = 'covidCases'


class AnalysisNameList:
    PRICE_PCT_CHANGE_WEEKLY = WEEKLY_KEY + '_change'
    PRICE_PCT_CHANGE_MONTHLY = MONTHLY_KEY + '_change'
    PRICE_PCT_CHANGE_YEARLY = YEARLY_KEY + '_change'
    ALPHA_MONTHLY = MONTHLY_KEY + '_alpha'
    ALPHA_YEARLY = YEARLY_KEY + '_alpha'


color_set = ['k', 'b', 'g', 'c', 'r', 'm']


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
    analysis_dict: dict
    pass


class Analyst:
    def __init__(self, fetcher: PropertyFetcher):
        self.table_dict = dict()
        self.strategy_report_list = list()
        self.fetcher = fetcher

    def reset(self):
        self.strategy_report_list = list()

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

        self.table_dict.update({table_name: df_file})

    def write_report(self, strategist: Strategist):
        if strategist.state is None:
            return
        if not (TableNameList.STOCK_PRICE in self.table_dict.keys()):
            return

        total_initial = 1
        total_history = pd.Series(dtype=float, name=strategist.name)

        for segment in strategist.state:
            segment_start_date = segment.start_date.strftime('%Y-%m-%d')
            segment_end_date = segment.end_date.strftime('%Y-%m-%d')
            symbols = segment.get_asset_symbol_list()
            df_price_table = self.table_dict[TableNameList.STOCK_PRICE]
            df_segment_price_history = df_price_table[segment_start_date:segment_end_date][symbols]
            df_segment_price_history.dropna(axis=1, inplace=True)
            initial_price_list = df_segment_price_history.iloc[0]
            holding_list = initial_price_list.apply(lambda x: total_initial / x / len(initial_price_list))
            segment_series = df_segment_price_history.apply(lambda x: x.dot(holding_list), axis=1)
            total_history = pd.concat([total_history, segment_series[:-1]])
            total_initial = segment_series[-1]
        total_history.rename(strategist.name,inplace=True)
        report = StrategyReport(name=strategist.name, account_history=total_history, segment_list=strategist.state,
                                analysis_dict={}, color=color_set[len(self.strategy_report_list)])

        resample_period_dict = {MONTHLY_KEY: '1M', YEARLY_KEY: '1Y'}
        price_change_period_dict = {MONTHLY_KEY: AnalysisNameList.PRICE_PCT_CHANGE_MONTHLY,
                                    YEARLY_KEY: AnalysisNameList.PRICE_PCT_CHANGE_YEARLY}
        alpha_period_dict = {MONTHLY_KEY: AnalysisNameList.ALPHA_MONTHLY,
                             YEARLY_KEY: AnalysisNameList.ALPHA_YEARLY}

        for period_key in resample_period_dict.keys():
            pct_change_history = total_history.resample(resample_period_dict[period_key]).mean().pct_change()[1:]
            analysis_seed_date = total_history.index[0]

            analysis_name = price_change_period_dict[period_key]
            report.analysis_dict.update({analysis_name: {analysis_seed_date: pct_change_history}})

            analysis_name = alpha_period_dict[period_key]
            market_history = self.table_dict[TableNameList.MARKET_INDEX]['^GSPC']
            market_pct_change_history = market_history.resample(resample_period_dict[period_key]).mean().pct_change()
            alpha_history = (pct_change_history - market_pct_change_history).dropna()
            report.analysis_dict.update({analysis_name: {analysis_seed_date: alpha_history}})

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
            report.analysis_dict.update({property_key: property_values_history})

    def get_report(self, name: str, report_recipe: ReportRecipe) -> StrategyReport:
        pass

    def draw_price_history(self):
        # plt.subplots(constrained_layout=True, figsize=(5, ))

        # plt.subplot(2, 1, 1)
        # plt.gca().set_title("Account history")

        for report in self.strategy_report_list:
            plt.plot(report.account_history, report.color, label=report.name, )

        # market_history = self.table_dict[TableNameList.MARKET_INDEX]['^GSPC'][report.account_history.index]
        # market_history /= market_history.iloc[0]
        # plt.plot(market_history / market_history.iloc[0], 'k', label='MarketAverage')

        plt.legend()

        # plt.subplot(2, 1, 2)
        # plt.gca().set_title("Monthly alpha")
        # for report in self.strategy_report_list:
        #     alpha_monthly_history = list(report.analysis_dict[AnalysisNameList.ALPHA_MONTHLY].values())[0]
        #     plt.plot(alpha_monthly_history, report.color, label=report.name, marker='o', linewidth=0.5, markersize=0.1)
        # plt.legend()

    def draw_property_distributions(self):

        plt.subplots(constrained_layout=True, figsize=(5, 10))
        report_list = self.strategy_report_list
        if not report_list:
            return
        registered_property_list = list(report_list[0].analysis_dict.keys())
        n_property = len(registered_property_list)
        for n in range(n_property):
            plt.subplot(n_property, 1, n + 1)

            property_key = registered_property_list[n]
            plt.gca().set_title(property_key)

            property_distribution_list = []
            for report in self.strategy_report_list:
                property_distribution = []
                property_value_series_list = list(report.analysis_dict[property_key].values())
                for property_value_series in property_value_series_list:
                    property_value_series.dropna(inplace=True)
                    property_distribution += property_value_series.values.tolist()
                property_distribution_list.append(property_distribution)

            box_plot = plt.boxplot(property_distribution_list,
                                   showfliers=False,
                                   notch=True, patch_artist=True, widths=0.6, whis=0);

            for box, report in zip(box_plot['boxes'], self.strategy_report_list):
                box.set_facecolor(report.color)

        pass

    def draw_correlation_heatmap(self, target_history_list_dict: dict[list], start_date: datetime.date,
                                 end_date: datetime.date):
        history_list = [report.account_history for report in self.strategy_report_list]
        pd.concat(history_list, axis=1)

        for key, value in target_history_list_dict.items():
            history_list.append(self.table_dict[key][value])

        df_concat = pd.concat(history_list, axis=1)
        df_concat = df_concat.loc[start_date:end_date]

        import seaborn as sns
        sns.heatmap(df_concat.corr(), annot=True, linewidths=.5);
