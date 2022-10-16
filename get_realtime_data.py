from os import access
import requests
from datetime import datetime, timedelta
import pandas as pd
import account_info
import streamlit as st

API_KEY = "ayNClqmZuOOBeL6lFjA348UfsA0jpzazy8pjyXsQ"

API_IDS = {'wind': 'EBA.MISO-ALL.NG.WND.H',
        'solar': 'EBA.MISO-ALL.NG.SUN.H',
        'hydro': 'EBA.MISO-ALL.NG.WAT.H',
        'coal': 'EBA.MISO-ALL.NG.COL.H',
        'natural_gas': 'EBA.MISO-ALL.NG.NG.H',
        'nuclear': 'EBA.MISO-ALL.NG.NUC.H',
        'other': 'EBA.MISO-ALL.NG.OTH.H'}

HEADERS = {'Content-Type': 'application/json'}

PP_ELECTRIC_PURCH = 'PP_Electric_Purch'

CO2_POUNDS_PER_MWH = {'coal': 2230, 'natural_gas': 910}

# CO2 Emission Calculations
HEAT_CONVERSION_COEFFS = { 'natural_gas': 1.026, 'pellets': 20.89375, 'oat_hulls': 8.25, 'coal': 24.93 }
CO2_CONVERSION_COEFFS = {  'natural_gas': 54.16, 'pellets': 136.025, 'oat_hulls': 154.37, 'coal': 105.88}
PURCH_CO2_COEFF = 611.169

USERNAME = st.secrets['username']
PASSWORD = st.secrets['password']

def get_response(series_id, start):
    url = f'https://api.eia.gov/series/?api_key=ayNClqmZuOOBeL6lFjA348UfsA0jpzazy8pjyXsQ&series_id={series_id}&start={start}'
    response = requests.get(url)
    return response.json()

def get_miso_electricity_data():
    now = datetime.now()
    # Get the time 24 hours ago
    time_24_hours_ago = now - timedelta(hours=24)
    # Convert to format YYYMMDDTHHZ
    time_24_hours_ago = time_24_hours_ago.strftime("%Y%m%dT%HZ")

    responses = {}
    for name, series_id in API_IDS.items():
        responses[name] = get_response(series_id, time_24_hours_ago)

    electricity_breakdown = {}
    for name, response in responses.items():
        data = response['series'][0]['data']
        times = [x[0] for x in data]
        values = [x[1] for x in data]
        recent_value = values[0]
        electricity_breakdown[name] = recent_value
    
    return electricity_breakdown

def get_grid_emissions():
    electricity_breakdown = get_miso_electricity_data()
    electricity_breakdown_percentages = {}
    # convert the values to percentages
    total = sum(electricity_breakdown.values())
    for key, value in electricity_breakdown.items():
        electricity_breakdown_percentages[key] = value / total
    latest_main_purch_el = get_latest_pi_data(PP_ELECTRIC_PURCH)['Value']
    # print(f'Latest main purch el: {latest_main_purch_el}')
    emissions = {}
    # get MWH from coal
    emissions['Coal'] = latest_main_purch_el * electricity_breakdown_percentages['coal']
    # print(f'Coal MWH: {coal_mwh}')
    # get MWH from natural gas
    emissions['Natural Gas'] = latest_main_purch_el * electricity_breakdown_percentages['natural_gas']
    # print(f'Natural gas MWH: {natural_gas_mwh}')
    # get CO2 from coal
    emissions['Coal'] = [emissions['Coal'] * CO2_POUNDS_PER_MWH['coal']]
    # get CO2 from natural gas
    emissions['Natural Gas'] = [emissions['Natural Gas'] * CO2_POUNDS_PER_MWH['natural_gas']]
    # Create a dataframe from emissions with columns as keys and rows as values
    df_emissions = pd.DataFrame.from_dict(emissions, orient="index", columns=["Emissions"])
    # make the index a column
    df_emissions.reset_index(inplace=True)
    # rename the index column
    df_emissions.rename(columns={"index": "Category"}, inplace=True)
    return df_emissions

def get_latest_pi_data(name):
    base_url = 'https://itsnt2259.iowa.uiowa.edu/piwebapi/search/query?q=name:'
    url = base_url + name
    # USERNAME, PASSWORD = account_info.getLogin()
    query = requests.get(url, auth=(USERNAME, PASSWORD), headers=HEADERS).json()
    self_url = query['Items'][0]['Links']['Self']
    point = requests.get(self_url, auth=(USERNAME, PASSWORD), headers=HEADERS).json()
    data_url = point['Links']['Value']
    data = requests.get(data_url, auth=(USERNAME, PASSWORD), headers=HEADERS).json()
    return data

def get_generated_emissions():
    '''returns current total generated co2'''
    coal_pellet = toCO2_coal_pellet()
    pellet = toCO2_pellets()
    ng = toCO2_ng()
    oat_hulls = toCO2_oat_hulls()
    emissions = {'Coal Pellet': coal_pellet, 'Pellet': pellet, 'Natural Gas': ng, 'Oat Hulls': oat_hulls}
    emissions_df = pd.DataFrame.from_dict(emissions, orient="index", columns=["Emissions"])
    emissions_df.reset_index(inplace=True)
    emissions_df.rename(columns={"index": "Category"}, inplace=True)
    return emissions_df

def toCO2_ng():
    main_ng_names = ['PP_TB1_2_TB1_GAS_FLOW', 'HBLR_GAS_FLOW', 'PP_B7_Gas_Flow_Adj', 'PP_B8_Gas_Flow_Adj', 'PP_B10_FLT_235_FT', 'PP_BLR12_FT_006_KSCFH',
                 'PP_GG1_FUEL_FLOW', 'PP_GG2_FUEL_FLOW', 'PP_GG3_FUEL_FLOW', 'PP_GG4_FUEL_FLOW', 'PP_AF-XI-8220A']
    total = 0.
    for i, name in enumerate(main_ng_names):
        latest = get_latest_pi_data(name)
        # add columns 1,2,3,4,6,11 of main_ng_df to main_ng_df['Sum']
        if i in [0,1,2,3,5,10]:
            total += latest['Value'] * HEAT_CONVERSION_COEFFS['natural_gas'] * CO2_CONVERSION_COEFFS['natural_gas']
        # add columns 5,7,8,9,10 of main_ng_df to main_ng_df['CO2']
        else:
            total += latest['Value']/1000 * HEAT_CONVERSION_COEFFS['natural_gas'] * CO2_CONVERSION_COEFFS['natural_gas']
    return total

def toCO2_pellets():
    lastest_pellets = get_latest_pi_data('PP_CHS_B10WeighBelt_MvgAvg')['Value'] / 2
    emissions = lastest_pellets * HEAT_CONVERSION_COEFFS['pellets'] * CO2_CONVERSION_COEFFS['pellets']
    return emissions

def toCO2_oat_hulls():
    lastest_oat_hulls = get_latest_pi_data('PP_BIO_Weight')['Value'] / 2
    emissions = lastest_oat_hulls * HEAT_CONVERSION_COEFFS['oat_hulls'] * CO2_CONVERSION_COEFFS['oat_hulls']
    return emissions

def toCO2_coal_pellet():
    CURRENT_PELLET_PERCENT = 0.195
    lastest_coal_pellet = get_latest_pi_data('PP_SF-WIT-6044A')['Value'] / 2
    emissions = lastest_coal_pellet * (HEAT_CONVERSION_COEFFS['pellets'] * CURRENT_PELLET_PERCENT * CO2_CONVERSION_COEFFS['pellets'] +
                                        HEAT_CONVERSION_COEFFS['coal'] * (1 - CURRENT_PELLET_PERCENT) * CO2_CONVERSION_COEFFS['coal'])
    return emissions
        
# print(get_generated_emissions())
