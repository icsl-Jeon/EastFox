from aenum import StrEnum, skip, auto


def get_all_sub_tables(table_key: StrEnum) -> list[str]:
    return list(vars(table_key)['_value2member_map_'].keys())


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
        PBR = 'priceBookValueRatio'
        PER = 'priceEarningsRatio'
        PCR = 'priceToFreeCashFlowsRatio'
        PSR = 'priceToSalesRatio'
        DEBT_RATIO = 'debtRatio'
        DIVIDEND_YIELD = 'dividendYield'

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
