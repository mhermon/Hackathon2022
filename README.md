# Hackathon2022
Hackathon project for UIOWA Hackathon 2022.   
Group Members: Mitchell Hermon, Raymond Yang, Maneesh John, Julian Wemmie

## Description
UIOWA Hackathon Engie Challenge. There are three parts to the challenge and our app. The first section correlates historical campus energy load with generated emissions. The second section shows historical energy and emissions data. The third section provides a prediction for future campus electricity load using a deep learning model implemented in Tensorflow/Keras.

## Installation
Install Requirements   
`pip install -r requirements.txt`

Run Streamlit   
`streamlit run app.py`

Requires UIOWA login in order to access PI API.   
In directory `.streamlit/secrets.toml` :   
`username = "<your-username>"`   
`password = "<your-password>"`

