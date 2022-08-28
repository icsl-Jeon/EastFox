import datetime
from enum import Enum
from dataclasses import dataclass
import pandas as pd
from typing import Union
from fetch import PropertyFetcher, PropertyNameList


class SelectorValue:
    PROFILE_SECTOR_INDUSTRIALS = 'Industrials'
    PROFILE_SECTOR_HEALTH_CARE = 'Health Care'
    PROFILE_SECTOR_INFORMATION_TECHNOLOGY = 'Information Technology'
    PROFILE_SECTOR_COMMUNICATION_SERVICES = 'Communication Services'
    PROFILE_SECTOR_CONSUMER_STAPLES = 'Consumer Staples'
    PROFILE_SECTOR_CONSUMER_DISCRETIONARY = 'Consumer Discretionary'
    PROFILE_SECTOR_UTILITIES = 'Utilities'
    PROFILE_SECTOR_FINANCIALS = 'Financials'
    PROFILE_SECTOR_MATERIALS = 'Materials'
    PROFILE_SECTOR_REAL_ESTATE = 'Real Estate'
    PROFILE_SECTOR_ENERGY = 'Energy'
    PROFILE_INDUSTRY_INDUSTRIAL_CONGLOMERATES = 'Industrial Conglomerates'
    PROFILE_INDUSTRY_BUILDING_PRODUCTS = 'Building Products'
    PROFILE_INDUSTRY_HEALTH_CARE_EQUIPMENT = 'Health Care Equipment'
    PROFILE_INDUSTRY_PHARMACEUTICALS = 'Pharmaceuticals'
    PROFILE_INDUSTRY_IT_CONSULTING_OTHER_SERVICES = 'IT Consulting & Other Services'
    PROFILE_INDUSTRY_INTERACTIVE_HOME_ENTERTAINMENT = 'Interactive Home Entertainment'
    PROFILE_INDUSTRY_AGRICULTURAL_PRODUCTS = 'Agricultural Products'
    PROFILE_INDUSTRY_APPLICATION_SOFTWARE = 'Application Software'
    PROFILE_INDUSTRY_DATA_PROCESSING_OUTSOURCED_SERVICES = 'Data Processing & Outsourced Services'
    PROFILE_INDUSTRY_AUTOMOTIVE_RETAIL = 'Automotive Retail'
    PROFILE_INDUSTRY_INDEPENDENT_POWER_PRODUCERS_ENERGY_TRADERS = 'Independent Power Producers & Energy Traders'
    PROFILE_INDUSTRY_LIFE_HEALTH_INSURANCE = 'Life & Health Insurance'
    PROFILE_INDUSTRY_INDUSTRIAL_GASES = 'Industrial Gases'
    PROFILE_INDUSTRY_INTERNET_SERVICES_INFRASTRUCTURE = 'Internet Services & Infrastructure'
    PROFILE_INDUSTRY_AIRLINES = 'Airlines'
    PROFILE_INDUSTRY_SPECIALTY_CHEMICALS = 'Specialty Chemicals'
    PROFILE_INDUSTRY_OFFICE_REITS = 'Office REITs'
    PROFILE_INDUSTRY_HEALTH_CARE_SUPPLIES = 'Health Care Supplies'
    PROFILE_INDUSTRY_ELECTRIC_UTILITIES = 'Electric Utilities'
    PROFILE_INDUSTRY_PROPERTY_CASUALTY_INSURANCE = 'Property & Casualty Insurance'
    PROFILE_INDUSTRY_INTERACTIVE_MEDIA_SERVICES = 'Interactive Media & Services'
    PROFILE_INDUSTRY_TOBACCO = 'Tobacco'
    PROFILE_INDUSTRY_INTERNET_DIRECT_MARKETING_RETAIL = 'Internet & Direct Marketing Retail'
    PROFILE_INDUSTRY_PAPER_PACKAGING = 'Paper Packaging'
    PROFILE_INDUSTRY_SEMICONDUCTORS = 'Semiconductors'
    PROFILE_INDUSTRY_MULTI_UTILITIES = 'Multi-Utilities'
    PROFILE_INDUSTRY_CONSUMER_FINANCE = 'Consumer Finance'
    PROFILE_INDUSTRY_SPECIALIZED_REITS = 'Specialized REITs'
    PROFILE_INDUSTRY_WATER_UTILITIES = 'Water Utilities'
    PROFILE_INDUSTRY_ASSET_MANAGEMENT_CUSTODY_BANKS = 'Asset Management & Custody Banks'
    PROFILE_INDUSTRY_HEALTH_CARE_DISTRIBUTORS = 'Health Care Distributors'
    PROFILE_INDUSTRY_ELECTRICAL_COMPONENTS_EQUIPMENT = 'Electrical Components & Equipment'
    PROFILE_INDUSTRY_BIOTECHNOLOGY = 'Biotechnology'
    PROFILE_INDUSTRY_ELECTRONIC_COMPONENTS = 'Electronic Components'
    PROFILE_INDUSTRY_INSURANCE_BROKERS = 'Insurance Brokers'
    PROFILE_INDUSTRY_OIL_GAS_EXPLORATION_PRODUCTION = 'Oil & Gas Exploration & Production'
    PROFILE_INDUSTRY_TECHNOLOGY_HARDWARESTORAGE_PERIPHERALS = 'Technology Hardware, Storage & Peripherals'
    PROFILE_INDUSTRY_SEMICONDUCTOR_EQUIPMENT = 'Semiconductor Equipment'
    PROFILE_INDUSTRY_AUTO_PARTS_EQUIPMENT = 'Auto Parts & Equipment'
    PROFILE_INDUSTRY_COMMUNICATIONS_EQUIPMENT = 'Communications Equipment'
    PROFILE_INDUSTRY_MULTI_LINE_INSURANCE = 'Multi-line Insurance'
    PROFILE_INDUSTRY_INTEGRATED_TELECOMMUNICATION_SERVICES = 'Integrated Telecommunication Services'
    PROFILE_INDUSTRY_GAS_UTILITIES = 'Gas Utilities'
    PROFILE_INDUSTRY_SPECIALTY_STORES = 'Specialty Stores'
    PROFILE_INDUSTRY_RESIDENTIAL_REITS = 'Residential REITs'
    PROFILE_INDUSTRY_OIL_GAS_EQUIPMENT_SERVICES = 'Oil & Gas Equipment & Services'
    PROFILE_INDUSTRY_METAL_GLASS_CONTAINERS = 'Metal & Glass Containers'
    PROFILE_INDUSTRY_DIVERSIFIED_BANKS = 'Diversified Banks'
    PROFILE_INDUSTRY_MULTI_SECTOR_HOLDINGS = 'Multi-Sector Holdings'
    PROFILE_INDUSTRY_COMPUTER_ELECTRONICS_RETAIL = 'Computer & Electronics Retail'
    PROFILE_INDUSTRY_LIFE_SCIENCES_TOOLS_SERVICES = 'Life Sciences Tools & Services'
    PROFILE_INDUSTRY_AEROSPACE_DEFENSE = 'Aerospace & Defense'
    PROFILE_INDUSTRY_DISTILLERS_VINTNERS = 'Distillers & Vintners'
    PROFILE_INDUSTRY_AIR_FREIGHT_LOGISTICS = 'Air Freight & Logistics'
    PROFILE_INDUSTRY_CASINOS_GAMING = 'Casinos & Gaming'
    PROFILE_INDUSTRY_PACKAGED_FOODS_MEATS = 'Packaged Foods & Meats'
    PROFILE_INDUSTRY_HOTELSRESORTS_CRUISE_LINES = 'Hotels, Resorts & Cruise Lines'
    PROFILE_INDUSTRY_CONSTRUCTION_MACHINERY_HEAVY_TRUCKS = 'Construction Machinery & Heavy Trucks'
    PROFILE_INDUSTRY_FINANCIAL_EXCHANGES_DATA = 'Financial Exchanges & Data'
    PROFILE_INDUSTRY_REAL_ESTATE_SERVICES = 'Real Estate Services'
    PROFILE_INDUSTRY_TECHNOLOGY_DISTRIBUTORS = 'Technology Distributors'
    PROFILE_INDUSTRY_MANAGED_HEALTH_CARE = 'Managed Health Care'
    PROFILE_INDUSTRY_FERTILIZERS_AGRICULTURAL_CHEMICALS = 'Fertilizers & Agricultural Chemicals'
    PROFILE_INDUSTRY_INVESTMENT_BANKING_BROKERAGE = 'Investment Banking & Brokerage'
    PROFILE_INDUSTRY_CABLE_SATELLITE = 'Cable & Satellite'
    PROFILE_INDUSTRY_INTEGRATED_OIL_GAS = 'Integrated Oil & Gas'
    PROFILE_INDUSTRY_RESTAURANTS = 'Restaurants'
    PROFILE_INDUSTRY_HOUSEHOLD_PRODUCTS = 'Household Products'
    PROFILE_INDUSTRY_DIVERSIFIED_SUPPORT_SERVICES = 'Diversified Support Services'
    PROFILE_INDUSTRY_REGIONAL_BANKS = 'Regional Banks'
    PROFILE_INDUSTRY_SOFT_DRINKS = 'Soft Drinks'
    PROFILE_INDUSTRY_HYPERMARKETS_SUPER_CENTERS = 'Hypermarkets & Super Centers'
    PROFILE_INDUSTRY_RAILROADS = 'Railroads'
    PROFILE_INDUSTRY_INDUSTRIAL_MACHINERY = 'Industrial Machinery'
    PROFILE_INDUSTRY_HEALTH_CARE_SERVICES = 'Health Care Services'
    PROFILE_INDUSTRY_HOMEBUILDING = 'Homebuilding'
    PROFILE_INDUSTRY_HEALTH_CARE_FACILITIES = 'Health Care Facilities'
    PROFILE_INDUSTRY_AGRICULTURAL_FARM_MACHINERY = 'Agricultural & Farm Machinery'
    PROFILE_INDUSTRY_MOVIES_ENTERTAINMENT = 'Movies & Entertainment'
    PROFILE_INDUSTRY_GENERAL_MERCHANDISE_STORES = 'General Merchandise Stores'
    PROFILE_INDUSTRY_COMMODITY_CHEMICALS = 'Commodity Chemicals'
    PROFILE_INDUSTRY_INDUSTRIAL_REITS = 'Industrial REITs'
    PROFILE_INDUSTRY_DIVERSIFIED_CHEMICALS = 'Diversified Chemicals'
    PROFILE_INDUSTRY_RESEARCH_CONSULTING_SERVICES = 'Research & Consulting Services'
    PROFILE_INDUSTRY_PERSONAL_PRODUCTS = 'Personal Products'
    PROFILE_INDUSTRY_REINSURANCE = 'Reinsurance'
    PROFILE_INDUSTRY_RETAIL_REITS = 'Retail REITs'
    PROFILE_INDUSTRY_AUTOMOBILE_MANUFACTURERS = 'Automobile Manufacturers'
    PROFILE_INDUSTRY_SYSTEMS_SOFTWARE = 'Systems Software'
    PROFILE_INDUSTRY_COPPER = 'Copper'
    PROFILE_INDUSTRY_CONSUMER_ELECTRONICS = 'Consumer Electronics'
    PROFILE_INDUSTRY_LEISURE_PRODUCTS = 'Leisure Products'
    PROFILE_INDUSTRY_HEALTH_CARE_REITS = 'Health Care REITs'
    PROFILE_INDUSTRY_HOME_IMPROVEMENT_RETAIL = 'Home Improvement Retail'
    PROFILE_INDUSTRY_HOTEL_RESORT_REITS = 'Hotel & Resort REITs'
    PROFILE_INDUSTRY_ADVERTISING = 'Advertising'
    PROFILE_INDUSTRY_TRUCKING = 'Trucking'
    PROFILE_INDUSTRY_CONSTRUCTION_ENGINEERING = 'Construction & Engineering'
    PROFILE_INDUSTRY_ELECTRONIC_EQUIPMENT_INSTRUMENTS = 'Electronic Equipment & Instruments'
    PROFILE_INDUSTRY_OIL_GAS_STORAGE_TRANSPORTATION = 'Oil & Gas Storage & Transportation'
    PROFILE_INDUSTRY_FOOD_RETAIL = 'Food Retail'
    PROFILE_INDUSTRY_DISTRIBUTORS = 'Distributors'
    PROFILE_INDUSTRY_ALTERNATIVE_CARRIERS = 'Alternative Carriers'
    PROFILE_INDUSTRY_OIL_GAS_REFINING_MARKETING = 'Oil & Gas Refining & Marketing'
    PROFILE_INDUSTRY_CONSTRUCTION_MATERIALS = 'Construction Materials'
    PROFILE_INDUSTRY_HOME_FURNISHINGS = 'Home Furnishings'
    PROFILE_INDUSTRY_BREWERS = 'Brewers'
    PROFILE_INDUSTRY_HOUSEWARES_SPECIALTIES = 'Housewares & Specialties'
    PROFILE_INDUSTRY_GOLD = 'Gold'
    PROFILE_INDUSTRY_PUBLISHING = 'Publishing'
    PROFILE_INDUSTRY_APPARELACCESSORIES_LUXURY_GOODS = 'Apparel, Accessories & Luxury Goods'
    PROFILE_INDUSTRY_STEEL = 'Steel'
    PROFILE_INDUSTRY_ENVIRONMENTAL_FACILITIES_SERVICES = 'Environmental & Facilities Services'
    PROFILE_INDUSTRY_HUMAN_RESOURCE_EMPLOYMENT_SERVICES = 'Human Resource & Employment Services'
    PROFILE_INDUSTRY_APPAREL_RETAIL = 'Apparel Retail'
    PROFILE_INDUSTRY_FOOD_DISTRIBUTORS = 'Food Distributors'
    PROFILE_INDUSTRY_WIRELESS_TELECOMMUNICATION_SERVICES = 'Wireless Telecommunication Services'
    PROFILE_INDUSTRY_ELECTRONIC_MANUFACTURING_SERVICES = 'Electronic Manufacturing Services'
    PROFILE_INDUSTRY_TRADING_COMPANIES_DISTRIBUTORS = 'Trading Companies & Distributors'
    PROFILE_INDUSTRY_DRUG_RETAIL = 'Drug Retail'
    PROFILE_INDUSTRY_BROADCASTING = 'Broadcasting'
    PROFILE_INDUSTRY_HOUSEHOLD_APPLIANCES = 'Household Appliances'


class SelectorType(Enum):
    PROFILE = 0
    POINT_VALUE = 1
    HORIZON_RANGE = 2
    INCLUSION = 4


@dataclass
class Selector:
    type: SelectorType
    key: str
    value: Union[list[str], tuple[float, float]]
    horizon: int = 1
    is_absolute: bool = True


@dataclass
class SelectorSequence:
    selectors: list[Selector]


@dataclass
class Filter:
    name: str
    selector_sequence_union: list[SelectorSequence]


@dataclass
class Asset:
    symbol: str

    def __eq__(self, other):
        return self.symbol == other.symbol

    def __hash__(self):
        return hash(self.symbol)


@dataclass
class Segment:
    start_date: datetime.date
    end_date: datetime.date
    assets: list[Asset]

    def get_asset_symbol_list(self):
        return [asset.symbol for asset in self.assets]


class Strategist:
    def __init__(self, name: str, fetcher: PropertyFetcher,
                 asset_pool: list[Asset],
                 start_date: datetime.date, end_date: datetime.date) -> None:
        initial_segment = Segment(
            start_date=start_date, end_date=end_date, assets=asset_pool)
        self.name = name
        self.fetcher = fetcher
        self.state = [initial_segment]
        self.asset_pool = asset_pool
        pass

    def __apply_selector_sequence(self, selector_sequence: SelectorSequence, query_date: datetime.date) -> set[Asset]:
        asset_pool = self.asset_pool.copy()
        for selector in selector_sequence.selectors:

            table_dict = self.fetcher.table_dict
            symbol_list = [asset.symbol for asset in asset_pool]

            if selector.type == SelectorType.PROFILE:
                property_table = self.fetcher.table_dict[PropertyNameList.PROFILE]
                selected_row = property_table[property_table[PropertyNameList.SYMBOL].isin(symbol_list)]
                selected_assets = selected_row[selected_row[selector.key].isin(selector.value)][
                    PropertyNameList.SYMBOL].values.tolist()

            elif selector.type == SelectorType.HORIZON_RANGE:
                horizon_end = query_date.strftime('%Y-%m-%d')
                horizon_start = (query_date - datetime.timedelta(days=365 * selector.horizon)).strftime('%Y-%m-%d')

                mean_table_asset_pool: pd.Series = \
                    table_dict[selector.key][horizon_start:horizon_end][symbol_list].mean()

                if not selector.is_absolute:
                    mean_table_asset_pool = mean_table_asset_pool.rank(pct=True)

                selected_assets = mean_table_asset_pool[
                    mean_table_asset_pool.between(selector.value[0], selector.value[1])].index.tolist()
            else:
                selected_assets = []
                pass

            selected_assets.sort()
            asset_pool = [Asset(symbol=symbol) for symbol in selected_assets]

        return set(asset_pool)

    def select_assets(self, filter: Filter, rebalance_date: datetime.date):
        belong_idx = -1
        for idx, segment in enumerate(self.state):
            if (segment.start_date <= rebalance_date) & (rebalance_date <= segment.end_date):
                belong_idx = idx
                break
        if belong_idx < 0:
            print('filter time location is not valid')
            return

        filtered_assets = set()
        for selector_sequence in filter.selector_sequence_union:
            assets_from_selector_sequence \
                = self.__apply_selector_sequence(selector_sequence, rebalance_date)
            filtered_assets = filtered_assets.union(assets_from_selector_sequence)

        asset_list_sorted = [asset.symbol for asset in list(filtered_assets)]
        asset_list_sorted.sort()
        filtered_assets = [Asset(symbol=symbol) for symbol in asset_list_sorted]
        shrink_segment = self.state[belong_idx]
        inserted_segment = Segment(start_date=rebalance_date, end_date=shrink_segment.end_date,
                                   assets=list(filtered_assets))
        shrink_segment.end_date = rebalance_date
        self.state[belong_idx] = shrink_segment
        self.state.insert(belong_idx + 1, inserted_segment)

    def show_asset_selection(self):
        asset_selected = []
        from collections import Counter

        for segment in self.state:
            asset_selected += segment.get_asset_symbol_list()

        asset_counts = Counter(asset_selected)
        sorted_counts = pd.Series(asset_counts, name="select count").sort_index()
        sorted_counts = sorted_counts[sorted_counts > 1]
        profile_table = self.fetcher.table_dict[PropertyNameList.PROFILE].set_index(
            PropertyNameList.SYMBOL).sort_index()
        selected_profile_table = profile_table.loc[sorted_counts.index.values]
        selected_profile_table.insert(0, "selectCounts", sorted_counts)

        return selected_profile_table
