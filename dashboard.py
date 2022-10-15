import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import os
import plotly.graph_objects as go

BASE_DIR = os.getcwd()

#img = Image.open(os.path.join(BASE_DIR, 'images', 'ENGIE-Logo-Gradient-Blue-Full.png'))
# st.image(os.path.join(BASE_DIR, 'images', 'ENGIE-Logo-Gradient-Blue-Full.png'), width=200)

st.set_page_config(
    page_title="Carbon Footprint Data Visualization",
    page_icon="✅",
    layout="wide",
)

st.title("Carbon Footprint Emission Visualization")

# Streamlit Dashboard
st.write("1-Year Historical Emissions")
# We need data here from level 1

st.write("Real-Time Emission Dashboard")

# labels = ['Renewable', 'Coal', 'Natural Gas', 'Nuclear', 'Other']
# sizes = [15, 30, 45, 10, 10]
# # pie chart
# fig1, ax1 = plt.subplots()
# ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
#         shadow=True, startangle=90)
# ax1.axis('equal')

# st.pyplot(fig1)

fig =go.Figure(go.Sunburst(
    labels=["Eve", "Cain", "Seth", "Enos", "Noam", "Abel", "Awan", "Enoch", "Azura"],
    parents=["", "Eve", "Eve", "Seth", "Seth", "Eve", "Eve", "Awan", "Eve" ],
    values=[10, 14, 12, 10, 2, 6, 6, 4, 4],
))
fig.update_layout(margin = dict(t=0, l=0, r=0, b=0))

st.plotly_chart(fig)



'''
while True:
    # We need live data here
    pass
'''

