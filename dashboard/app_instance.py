# app_instance.py
# Imports
# Imports
import dash
import dash_bootstrap_components as dbc
from flask import Flask

# Create Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

# Flask server (optional)
server = app.server

app.title = "Dash App"


