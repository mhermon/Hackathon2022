import pickle
import streamlit as st
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
import pickle

def dashboard():
    st.title("Carbon Footprint Emissions - University of Iowa Main Campus")
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
    col1.header("Electrical Grid Energy Sources and Sustainability")
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
        fig2.update_layout(xaxis_title="Source of Energy", yaxis_title="Emissions (kgs CO2e)")
        fig2.update_layout(legend_title_text = "Energy Source")
        fig2.update_layout(template="plotly_white")

        col2.success("Done!")
        col2.header("Purchased Grid Electricity Emissions vs Generated Emissions")
        col2.plotly_chart(fig2, use_container_width=True)

        st.markdown("""---""")

def graph_historic_data(df, title, y_axis_1, y_axis_2, y_axis_title_1, y_axis_title_2):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=df['date'], y=df[y_axis_1], name=y_axis_title_1),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(x=df['date'], y=df[y_axis_2], name=y_axis_title_2),
        secondary_y=True,
    )
    fig.update_layout(
        title_text=title,
        title_x = 0.5
    )
    fig.update_xaxes(title_text="Time")
    fig.update_yaxes(title_text=y_axis_title_1, secondary_y=False)
    fig.update_yaxes(title_text=y_axis_title_2, secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

def graph_breakdown(df):
    fig = px.line(df, x = df['date'], y = df.columns[1:6])
    fig.update_layout(title_text = 'Emissions for Generated Electricity by Fuel Type', title_x = 0.5)
    fig.update_layout(legend_title_text = "Energy Source")
    fig.update_xaxes(title_text = 'Time')
    fig.update_yaxes(title_text = 'CO2 Emissions (Kg)')
    st.plotly_chart(fig, use_container_width = True)

def historical():
    st.header("One-Year Historical Load and Emission Data")
    historic_miso_emissions = ghd.get_historical_miso_co2_data()
    graph_historic_data(historic_miso_emissions, 'Purchased Electricity vs Emissions' , 'PP_Electric_Purch', 'emissions', 'Purchased Electricity (MWh)', 'CO2 Emissions (Kg)')
    gen_historical_emissions = ghd.get_gen_historical_emissions()
    graph_historic_data(gen_historical_emissions, 'Generated Electricity vs Emissions' , 'Generated', 'Total Emissions', 'Generated Electricity (MWh)', 'CO2 Emissions (Kg)')
    graph_breakdown(gen_historical_emissions)

# def login(username, password):
#     base_url = 'https://itsnt2259.iowa.uiowa.edu/piwebapi/search/query'
#     url = base_url
#     query = requests.get(url, auth=(username, password))
#     if query.status_code != 200:
#         st.warning("Login Error")
#         return
#     account_info.setLogin(username, password)
#     st.success("Login Successful!")

# def toggle_login():
#     st.title("Dashboard Login")
#     placeholder = st.empty()
#     with placeholder.container():
#         username = st.text_input("UIOWA Username or Email")
#         password = st.text_input("UIOWA Password", type="password")
#         # st.session_state['username'] = username
#         # st.session_state['password'] = password

#         btn = st.button("Login")
#         if btn:
#             login(username, password)

# Driver Code
st.set_page_config(
    page_title="Carbon Footprint Data Visualization",
    page_icon="🌎",
    layout="wide",
)

page_names_to_funcs = {
    # "Login Page": toggle_login,
    "Real-Time Dashboard": dashboard,
    "Historical Analysis": historical,
}

selected_page = st.sidebar.selectbox("Select a page", page_names_to_funcs.keys())
page_names_to_funcs[selected_page]()