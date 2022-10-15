import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import get_realtime_data as grt

st.set_page_config(
    page_title="Carbon Footprint Data Visualization",
    page_icon="✅",
    layout="wide",
)

st.title("Carbon Footprint Emission Visualization")

st.write("1-Year Historical Emissions")

st.write("Real-Time Emission Dashboard")

data = grt.get_miso_electricity_data()
sumEnergy = data['wind'] + data['solar'] + data['hydro'] + data['coal'] + data['natural_gas'] + data['nuclear'] + data['other']
sumClean = data['wind'] + data['solar'] + data['hydro'] + data['nuclear']
sumDirty = data['natural_gas'] + data['coal']
sumOther = data['other']

pc = dict()
for key, val in data.items():
    pc[key] = round(val/sumEnergy * 100)

pcClean = pc['wind'] + pc['solar'] + pc['hydro'] + pc['nuclear']
pcDirty = pc['natural_gas'] + pc['coal']

print(pc)
print(sum(pc.values()))

st.slider("Select a year", 2019, 2020, 2020)

fig =go.Figure(go.Sunburst(
    labels=["Grid Electricity", "Clean Energy", "Dirty Energy", "Coal", "Natural Gas", "Wind", "Nuclear", "Solar", "Hydro", "Other"],
    parents=["", "Grid Electricity", "Grid Electricity", "Dirty Energy", "Dirty Energy", "Clean Energy", "Clean Energy", "Clean Energy", "Clean Energy", "Grid Electricity"],
    branchvalues="total",
    values=[sum(pc.values()), pcClean, pcDirty, pc['coal'], pc['natural_gas'], pc['wind'], pc['nuclear'], pc['solar'], pc['hydro'], pc['other']]
))
fig.update_layout(margin = dict(t=0, l=0, r=0, b=0))
fig.update_traces(textinfo="label+percent parent")

st.plotly_chart(fig)