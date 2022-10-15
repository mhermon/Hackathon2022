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

def get_response(series_id, start):
    url = f'https://api.eia.gov/series/?api_key={API_KEY}&series_id={series_id}&start={start}'
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
    print(f'Latest main purch el: {latest_main_purch_el}')
    # get MWH from coal
    coal_mwh = latest_main_purch_el * electricity_breakdown_percentages['coal']
    print(f'Coal MWH: {coal_mwh}')
    # get MWH from natural gas
    natural_gas_mwh = latest_main_purch_el * electricity_breakdown_percentages['natural_gas']
    print(f'Natural gas MWH: {natural_gas_mwh}')
    # get CO2 from coal
    coal_co2 = coal_mwh * CO2_POUNDS_PER_MWH['coal']
    # get CO2 from natural gas
    natural_gas_co2 = natural_gas_mwh * CO2_POUNDS_PER_MWH['natural_gas']
    return {'coal': coal_co2, 'natural_gas': natural_gas_co2}

def get_latest_pi_data(name):
    base_url = 'https://itsnt2259.iowa.uiowa.edu/piwebapi/search/query?q=name:'
    url = base_url + name
    query = requests.get(url, auth=(USERNAME, PASSWORD), HEADERS=HEADERS).json()
    self_url = query['Items'][0]['Links']['Self']
    point = requests.get(self_url, auth=(USERNAME, PASSWORD), HEADERS=HEADERS).json()
    data_url = point['Links']['Value']
    data = requests.get(data_url, auth=(USERNAME, PASSWORD), HEADERS=HEADERS).json()
    return data