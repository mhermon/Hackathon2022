import os
from random import randint
import time
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import get_realtime_data as grt
import plotly.express as px
import requests
import account_info
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import get_historic_data as ghd

logged_in = False

st.set_page_config(
    page_title="Carbon Footprint Data Visualization",
    page_icon="🌎",
    layout="wide",
)

st.title("Dashboard Login")

def output_data():
    st.markdown("""---""")
    st.title("Carbon Footprint Emission Visualization")
    st.header("Real-Time Dashboards")
    placeholder = st.empty()
    with placeholder.container():
        btn = st.button("Update Dashboards")
    if btn:
        st.experimental_rerun()

    col1, col2 = st.columns(2)

    with st.spinner('Retrieving data...'):
        data = grt.get_miso_electricity_data()
        sumEnergy = data['wind'] + data['solar'] + data['hydro'] + data['coal'] + data['natural_gas'] + data['nuclear'] + data['other']

        pc = dict()
        for key, val in data.items():
            pc[key] = round(val/sumEnergy * 100)

        pcClean = pc['wind'] + pc['solar'] + pc['hydro'] + pc['nuclear']
        pcDirty = pc['natural_gas'] + pc['coal']

        color_discrete_sequence = ['', '#D62519', '#4A20F0','#E34922','#F0501F','#7110F0', '#7811F0', '#2D13F0','#5F33F0','#4E4922','#4E4922']

        fig1 =go.Figure(go.Sunburst(
            labels=["Grid Electricity", "Dirty Energy", "Clean Energy", "Coal", "Natural Gas", "Wind", "Nuclear", "Solar", "Hydro", "Other Energy", "Other Energy Units"],
            parents=["", "Grid Electricity", "Grid Electricity", "Dirty Energy", "Dirty Energy", "Clean Energy", "Clean Energy", "Clean Energy", "Clean Energy", "Grid Electricity", "Other Energy"],
            branchvalues="total",
            values=[sum(pc.values()), pcDirty, pcClean, pc['coal'], pc['natural_gas'], pc['wind'], pc['nuclear'], pc['solar'], pc['hydro'], pc['other'], pc['other']],
            hoverinfo='skip',
            marker=dict(colors=color_discrete_sequence),))
        fig1.update_layout(margin = dict(t=0, l=0, r=0, b=0))
        fig1.update_traces(textinfo="label+percent parent")

    col1.success("Done!")
    col1.write("This dashboard shows the real-time electricity breakdown of grid energy.")
    col1.plotly_chart(fig1, use_container_width=True)

    with st.spinner('Retrieving data...'):
        df_grid_emissions = grt.get_grid_emissions()
        df_grid_emissions['Source'] = 'Purchased'
        df_gen_emissions = grt.get_generated_emissions()
        df_gen_emissions['Source'] = 'Generated'
        combined_df = pd.concat([df_grid_emissions, df_gen_emissions])
        fig2 = px.bar(combined_df, x="Source", y="Emissions", color="Category",
            color_discrete_map={'Coal':'#F0C492', 'Natural Gas':'#F09287', 'Coal Pellet':'#C4F09E', 'Pellet':'#A1D8F0', 'Oat Hulls':'#E6B7F0'},)
            # color_discrete_map={'Coal':'#5A5A5A', 'Natural Gas':'#FF6961', 'Coal Pellet':'#A7C7E7', 'Pellet':'#fdfd96', 'Oat Hulls':'blue'},)
        fig2.update_layout(xaxis_title="Category", yaxis_title="Emissions (kgs CO2e)")
        fig2.update_layout(template="plotly_white")

        col2.success("Done!")
        col2.write("This bar graph measures the emission breakdown of grid and generated energy.")
        col2.plotly_chart(fig2, use_container_width=True)

        st.markdown("""---""")

        run_historical_data()

def graph_historic_data(df, title, y_axis_1, y_axis_2, y_axis_title_1, y_axis_title_2, col):
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    # Add traces
    fig.add_trace(
        go.Scatter(x=df['date'], y=df[y_axis_1], name=y_axis_title_1),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=df['date'], y=df[y_axis_2], name=y_axis_title_2),
        secondary_y=True,
    )
    # Add figure title
    fig.update_layout(
        title_text=title
    )
    # Set x-axis title
    fig.update_xaxes(title_text="Time")
    # Set y-axes titles
    fig.update_yaxes(title_text=y_axis_title_1, secondary_y=False)
    fig.update_yaxes(title_text=y_axis_title_2, secondary_y=True)
    col.plotly_chart(fig, use_container_width=True)

def graph_breakdown(df):
    fig = px.line(df, x = df['date'], y = df.columns[1:6])
    fig.update_layout(title_text = 'Generated Emissions by Fuel Type')
    fig.update_xaxes(title_text = 'Time')
    fig.update_yaxes(title_text = 'Kg CO2')
    st.plotly_chart(fig)

def run_historical_data():
    st.header("One Year Historical Load and Emission Data")

    col1, col2 = st.columns(2)

    historic_miso_emissions = ghd.get_historical_miso_co2_data()
    graph_historic_data(historic_miso_emissions, 'Purchased Electricity vs Emissions' , 'PP_Electric_Purch', 'emissions', 'Purchased Electricity', 'Emissions', col1)
    gen_historical_emissions = ghd.get_gen_historical_emissions()
    graph_historic_data(gen_historical_emissions, 'Generated Electricity vs Emissions' , 'Generated', 'Total Emissions', 'Generated Electricity', 'Emissions', col2)
    graph_breakdown(gen_historical_emissions)

def login(username, password):
    account_info.setLogin(username, password)
    base_url = 'https://itsnt2259.iowa.uiowa.edu/piwebapi/search/query'
    url = base_url
    query = requests.get(url, auth=(username, password))
    if query.status_code != 200:
        st.warning("Login Error")
        return
    output_data()
    refresher(5)

def refresher(seconds):
    while True:
        mainDir = os.path.dirname(__file__)
        filePath = os.path.join(mainDir, 'refresh.py')
        with open(filePath, 'w') as f:
            f.write(f'# {randint(0, 10000)}')
        time.sleep(seconds)
        
def toggle_login():
    placeholder = st.empty()
    with placeholder.container():
        username = st.text_input("UIOWA Username")
        password = st.text_input("UIOWA Password", type="password")
        btn = st.button("Login")
        if btn:
            login(username, password)
    
# Driver Code
toggle_login()