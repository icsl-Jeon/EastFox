from aenum import StrEnum, skip, auto


def get_all_sub_tables(table_key: StrEnum) -> list[str]:
    return list(vars(table_key)['_value2member_map_'].keys())


ANNUAL_TAG = '_annual'
QUARTER_TAG = '_quarter'


class TableValue(StrEnum):
    class Exchange:
        AMEX = 'AMEX'
        NASDAQ = 'NASDAQ'
        NYSE = 'NYSE'

    class Sector:
        INDUSTRIALS = 'Industrials'
        HEALTH_CARE = 'Health Care'
        INFORMATION_TECHNOLOGY = 'Information Technology'
        COMMUNICATION_SERVICES = 'Communication Services'
        CONSUMER_STAPLES = 'Consumer Staples'
        CONSUMER_DISCRETIONARY = 'Consumer Discretionary'
        UTILITIES = 'Utilities'
        FINANCIALS = 'Financials'
        MATERIALS = 'Materials'
        REAL_ESTATE = 'Real Estate'
        ENERGY = 'Energy'


class TableKey(StrEnum):
    MARKET_CAPITALIZATION = 'marketCap'
    PRICE_HISTORY = 'adjClose'
    EXCHANGE = 'exchangeShortName'

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
        @skip
        class BalanceSheet(StrEnum):
            TOTAL_DEBT = 'totalDebt'

        @skip
        class IncomeStatement(StrEnum):
            NET_INCOME = 'netIncome'
            GROSS_PROFIT = 'grossProfit'
            REVENUE = 'revenue'
            EBITDA = 'ebitda'
