from aenum import StrEnum, skip, auto


def get_all_sub_tables(table_key: StrEnum) -> list[str]:
    return list(vars(table_key)['_value2member_map_'].keys())


ANNUAL_TAG = '_annual'
QUARTER_TAG = '_quarter'


class TableKey(StrEnum):
    MARKET_CAPITALIZATION = 'marketCap'

    @skip
    class Profile(StrEnum):
        SYMBOL = 'symbol'
        SECTOR = 'sector'
        INDUSTRY = 'subSector'
        NAME = 'name'

    @skip
    class PriceHistory(StrEnum):
        YEARLY = '1Y'
        MONTHLY = '1M'
        DAILY = '1d'

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
