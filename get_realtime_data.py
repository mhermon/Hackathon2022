import requests
from secrets import API_KEY
from datetime import datetime, timedelta

API_IDS = {'wind': 'EBA.MISO-ALL.NG.WND.H',
        'solar': 'EBA.MISO-ALL.NG.SUN.H',
        'hydro': 'EBA.MISO-ALL.NG.WAT.H',
        'coal': 'EBA.MISO-ALL.NG.COL.H',
        'natural_gas': 'EBA.MISO-ALL.NG.NG.H',
        'nuclear': 'EBA.MISO-ALL.NG.NUC.H',
        'other': 'EBA.MISO-ALL.NG.OTH.H'}

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