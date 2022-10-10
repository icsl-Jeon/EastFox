from enum import Enum


class StringEnum(str, Enum):

    def _generate_next_value_(name, start, count, last_values):
        return name

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class SectorEnum(StringEnum):
    BASIC_MATERIALS = 'Basic Materials'
    COMMUNICATION_SERVICES = 'Communication Services'
    CONSUMER_CYCLICAL = 'Consumer Cyclical'
    CONSUMER_DEFENSIVE = 'Consumer Defensive'
    ENERGY = 'Energy'
    FINANCIAL_SERVICES = 'Financial Services'
    HEALTHCARE = 'Healthcare'
    INDUSTRIALS = 'Industrials'
    REAL_ESTATE = 'Real Estate'
    TECHNOLOGY = 'Technology'
    UTILITIES = 'Utilities'
