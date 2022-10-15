import requests
from datetime import datetime, timedelta
import pandas as pd
from account_info import USERNAME, PASSWORD

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

START_TIME = '52w'
END_TIME = '1d'
INTERVAL = '1d'

def get_historical_pi_data(name, start_time, end_time, interval):
    base_url = 'https://itsnt2259.iowa.uiowa.edu/piwebapi/search/query?q=name:'
    url = base_url + name
    query = requests.get(url, auth=(USERNAME, PASSWORD), headers=HEADERS).json()
    self_url = query['Items'][0]['Links']['Self']
    point = requests.get(self_url, auth=(USERNAME, PASSWORD), headers=HEADERS).json()
    data_url = point['Links']['InterpolatedData']
    data_url = data_url + '/?startTime=-' + start_time + '&endTime=-' + end_time + '&interval=' + interval
    data = requests.get(data_url, auth=(USERNAME, PASSWORD), headers=HEADERS).json()
    return data


def get_historical_df(names, startTime, endTime, interval):
    df = pd.DataFrame()
    for i, name in enumerate(names):
        data = get_historical_pi_data(name, startTime, endTime, interval)
        items = data['Items']
        if i == 0:
            times = [datetime.strptime(item['Timestamp'][:-2], '%Y-%m-%dT%H:%M:%S.%f') for item in items]
            df['Time'] = times
        validateData = lambda x: x if (isinstance(x, (int, float)) and x >= 0) else 0
        vals = [validateData(item['Value']) for item in items]
        df[name] = pd.DataFrame(vals)
    return df

def get_historical_emissions():
    df = pd.DataFrame()
    blr11_pellets, blr11_coal = get_coal_pellets_historical_emissions()
    df['Time'] = get_historical_df(['PP_Electric_Purch'], START_TIME, END_TIME, INTERVAL)['Time']
    df['Purch'] = get_purch_historical_emissions()
    df['Pellets'] = get_pellets_historical_emissions() + blr11_pellets
    df['Oat Hulls'] = get_oat_hulls_historical_emissions()
    df['Coal'] = blr11_coal
    df['Natural Gas'] = get_ng_historical_emissions()
    return df

def get_purch_historical_emissions():
    main_purch_el_names = ['PP_Electric_Purch']
    main_purch_el_df = get_historical_df(main_purch_el_names, START_TIME, END_TIME, INTERVAL)
    main_purch_el_df['CO2'] = main_purch_el_df['PP_Electric_Purch'] * PURCH_CO2_COEFF
    return main_purch_el_df['CO2']

# def get_gen_historical_emissions():
#     main_gen_el_names = ['PP_Electric_Gen']
#     main_gen_el_df = get_historical_df(main_gen_el_names, START_TIME, END_TIME, INTERVAL)
#     return main_gen_el_df


def get_pellets_historical_emissions():
    # Blr 10 Pellets
    blr_10_pellets_names = ['PP_CHS_B10WeighBelt_MvgAvg']
    blr_10_pellets_df = get_historical_df(blr_10_pellets_names, START_TIME, END_TIME, INTERVAL)
    blr_10_pellets_df['CO2'] = blr_10_pellets_df['PP_CHS_B10WeighBelt_MvgAvg'] * HEAT_CONVERSION_COEFFS['pellets'] * CO2_CONVERSION_COEFFS['pellets']
    return blr_10_pellets_df['CO2']

def get_oat_hulls_historical_emissions():
    # Blr 11 Oat Hulls
    blr_11_oat_hulls_names = ['PP_BIO_Weight']
    blr_11_oat_hulls_df = get_historical_df(blr_11_oat_hulls_names, START_TIME, END_TIME, INTERVAL)
    blr_11_oat_hulls_df['CO2'] = blr_11_oat_hulls_df['PP_BIO_Weight'] * HEAT_CONVERSION_COEFFS['oat_hulls'] * CO2_CONVERSION_COEFFS['oat_hulls']
    return blr_11_oat_hulls_df['CO2']

def get_coal_pellets_historical_emissions():
    # Blr 11 Coal + Pellets
    blr_11_coal_pellets_names = ['PP_SF-WIT-6044A']
    blr_11_coal_pellets_df = get_historical_df(blr_11_coal_pellets_names, START_TIME, END_TIME, INTERVAL)
    percent_pellet_average = 0.2316
    blr_11_coal_pellets_df['CO2_pellets'] = blr_11_coal_pellets_df['PP_SF-WIT-6044A'] * percent_pellet_average * HEAT_CONVERSION_COEFFS['pellets'] * CO2_CONVERSION_COEFFS['pellets']
    blr_11_coal_pellets_df['CO2_coal'] = blr_11_coal_pellets_df['PP_SF-WIT-6044A'] * (1-percent_pellet_average) * HEAT_CONVERSION_COEFFS['coal'] * CO2_CONVERSION_COEFFS['coal']
    return blr_11_coal_pellets_df['CO2_pellets'], blr_11_coal_pellets_df['CO2_coal']

def get_ng_historical_emissions():
    main_ng_names = ['PP_TB1_2_TB1_GAS_FLOW', 'HBLR_GAS_FLOW', 'PP_B7_Gas_Flow_Adj', 'PP_B8_Gas_Flow_Adj', 'PP_B10_FLT_235_FT', 'PP_BLR12_FT_006_KSCFH',
                 'PP_GG1_FUEL_FLOW', 'PP_GG2_FUEL_FLOW', 'PP_GG3_FUEL_FLOW', 'PP_GG4_FUEL_FLOW', 'PP_AF-XI-8220A']
    main_ng_df = get_historical_df(main_ng_names, START_TIME, END_TIME, INTERVAL)
    # add columns 1,2,3,4,6,11 of main_ng_df to main_ng_df['Sum']
    main_ng_df['Sum'] = main_ng_df.iloc[:, 1:5].sum(axis=1) + main_ng_df.iloc[:, 6:12].sum(axis=1)
    # add columns 5,7,8,9,10 of main_ng_df to main_ng_df['CO2']
    main_ng_df['Sum'] += (main_ng_df.iloc[:, 5:6].sum(axis=1) + main_ng_df.iloc[:, 7:11].sum(axis=1))/1000

    main_ng_df['CO2'] = main_ng_df['Sum'] * HEAT_CONVERSION_COEFFS['natural_gas'] * CO2_CONVERSION_COEFFS['natural_gas']
    return main_ng_df['CO2']

# print(get_purch_historical_data())
print(get_historical_emissions())

