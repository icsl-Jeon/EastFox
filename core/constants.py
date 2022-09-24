from aenum import StrEnum, skip, auto


def get_all_sub_tables(table_key: StrEnum) -> list[str]:
    return list(vars(table_key)['_value2member_map_'].keys())


ANNUAL_TAG = '_annual'
QUARTER_TAG = '_quarter'
AVERAGE_TAG = '_average'
CHANGE_RATE_TAG = '_change_rate'
ONE_WEEK_AVERAGE_TAG = '_1w' + AVERAGE_TAG
ONE_MONTH_AVERAGE_TAG = '_1m' + AVERAGE_TAG
THREE_MONTH_AVERAGE_TAG = '_3m' + AVERAGE_TAG
SIX_MONTH_AVERAGE_TAG = '_6m' + AVERAGE_TAG
ONE_YEAR_AVERAGE_TAG = '_1y' + AVERAGE_TAG


class TableValue(StrEnum):
    class Exchange:
        AMEX = 'AMEX'
        NASDAQ = 'NASDAQ'
        NYSE = 'NYSE'

    class Sector(StrEnum):
        BASIC_MATERIALS = 'Basic Materials'
        COMMUNICATION_SERVICES = 'Communication Services'
        SERVICES = 'Services'
        CONSUMER_CYCLICAL = 'Consumer Cyclical'
        CONSUMER_DEFENSIVE = 'Consumer Defensive'
        ENERGY = 'Energy'
        FINANCIAL_SERVICES = 'Financial Services'
        HEALTHCARE = 'Healthcare'
        INDUSTRIALS = 'Industrials'
        REAL_ESTATE = 'Real Estate'
        TECHNOLOGY = 'Technology'
        UTILITIES = 'Utilities'


class TableKey(StrEnum):
    MARKET_CAPITALIZATION = 'marketCap'
    PRICE_HISTORY = 'adjClose'
    EXCHANGE = 'exchangeShortName'
    PRICE_HISTORY_ONE_WEEK_RESAMPLE = PRICE_HISTORY + ONE_WEEK_AVERAGE_TAG
    PRICE_HISTORY_ONE_MONTH_RESAMPLE = PRICE_HISTORY + ONE_MONTH_AVERAGE_TAG
    PRICE_HISTORY_THREE_MONTH_RESAMPLE = PRICE_HISTORY + THREE_MONTH_AVERAGE_TAG
    PRICE_HISTORY_ONE_YEAR_RESAMPLE = PRICE_HISTORY + ONE_YEAR_AVERAGE_TAG

    @skip
    class Profile(StrEnum):
        SYMBOL = 'symbol'
        SECTOR = 'sector'
        INDUSTRY = 'industry'
        NAME = 'name'
        EXCHANGE = 'exchangeShortName'
        TYPE = 'type'

    @skip
    class FinancialRatios(StrEnum):
        class Annual(StrEnum):
            PBR = 'priceBookValueRatio' + ANNUAL_TAG
            PER = 'priceEarningsRatio' + ANNUAL_TAG
            PCR = 'priceToFreeCashFlowsRatio' + ANNUAL_TAG
            PSR = 'priceToSalesRatio' + ANNUAL_TAG
            DEBT_RATIO = 'debtRatio' + ANNUAL_TAG
            DIVIDEND_YIELD = 'dividendYield' + ANNUAL_TAG

        class Quarter(StrEnum):
            PBR = 'priceBookValueRatio' + QUARTER_TAG
            PER = 'priceEarningsRatio' + QUARTER_TAG
            PCR = 'priceToFreeCashFlowsRatio' + QUARTER_TAG
            PSR = 'priceToSalesRatio' + QUARTER_TAG
            DEBT_RATIO = 'debtRatio' + QUARTER_TAG
            DIVIDEND_YIELD = 'dividendYield' + QUARTER_TAG

    @skip
    class FinancialStatements(StrEnum):
        class BalanceSheet(StrEnum):
            class Annual(StrEnum):
                TOTAL_DEBT = 'totalDebt' + ANNUAL_TAG

            class Quarter(StrEnum):
                TOTAL_DEBT = 'totalDebt' + QUARTER_TAG

        class IncomeStatement(StrEnum):
            class Annual(StrEnum):
                NET_INCOME = 'netIncome' + ANNUAL_TAG
                GROSS_PROFIT = 'grossProfit' + ANNUAL_TAG
                REVENUE = 'revenue' + ANNUAL_TAG
                EBITDA = 'ebitda' + ANNUAL_TAG

            class Quarter(StrEnum):
                NET_INCOME = 'netIncome' + QUARTER_TAG
                GROSS_PROFIT = 'grossProfit' + QUARTER_TAG
                REVENUE = 'revenue' + QUARTER_TAG
                EBITDA = 'ebitda' + QUARTER_TAG
