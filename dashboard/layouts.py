# Define Dash layout components (optional)
# layouts.py
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash import html

def create_login_modal():
    return dbc.Modal(
        [
            dbc.ModalBody(
                html.Div([
                    # Add logo or brand image
                    html.Img(src="/assets/logo.png", className="mb-4", style={'width': '200px', 'display': 'block', 'margin-left': 'auto', 'margin-right': 'auto'}),
                    #html.H2("RANFusion", className="text-center"),
                    dbc.Input(id="username-input", placeholder="Username", type="text", className="mb-2", style={'width': '100%'}),
                    dbc.Input(id="password-input", placeholder="Password", type="password", className="mb-2", style={'width': '100%'}),
                    # Remember me checkbox
                    dbc.Checkbox(id="remember-me-checkbox", label="Remember Me", className="mb-2"),
                    dbc.Button("Log In", id="login-button", className="w-100"),
                    html.Div(id="login-error-message", style={'color': 'red'}),
                ])
            ),
        ],
        id="login-modal",
        is_open=True 
    )

def login_layout():
    return html.Div([
        create_login_modal() 
    ])

def main_layout():
    return html.Div([
        create_sidebar(),
        html.Div(id='map-container', children=[
            html.Iframe(
                id='map',
                src="https://www.google.com/maps/embed?pb=...",  # Your Google Maps link here
                style={"height": "100%", "width": "100%"}
            )
        ], style={"height": "50vh"}),  # Initial height for map container

        html.Div(id='divider', children=[
            "Drag to resize"
        ], style={"height": "30px", "background": "grey", "cursor": "row-resize"}),

        html.Div(id='tabs-container', children=[
            dbc.Tabs(id="tabs", children=[
                dbc.Tab(label="UE Level Report", tab_id="tab-ue"),
                dbc.Tab(label="Cell Level Report", tab_id="tab-cell"),
                dbc.Tab(label="gNodeB Level Report", tab_id="tab-gnodb"),
                dbc.Tab(label="Network Level Report", tab_id="tab-network"),
            ], active_tab="tab-ue"),
            html.Div(id="tab-content")  # Content for selected tab
        ], style={"height": "calc(50vh - 30px)"})  # Adjust initial height for tabs container
    ])

def create_sidebar():
    return dbc.Nav(
        [
            dbc.NavLink("Home", href="/home", active="exact"),
            dbc.NavLink("Settings", href="/settings", active="exact"),
            # Add more links as needed
        ],
        vertical=True,
        pills=True,  # for active link styling
    )
def ue_level_report_layout():
    return html.Div([
        html.H3("UE Level Report"),
        # Add more components for UE Level Report here
    ])

def cell_level_report_layout():
    return html.Div([
        html.H3("Cell Level Report"),
        # Add more components for Cell Level Report here
    ])

def gnodb_level_report_layout():
    return html.Div([
        html.H3("gNodeB Level Report"),
        # Add more components for gNodeB Level Report here
    ])

def network_level_report_layout():
    return html.Div([
        html.H3("Network Level Report"),
        # Add more components for Network Level Report here
    ])

def create_sidebar():
    return dbc.Nav(
        [
            # Add your menu items here with dbc.NavLink...
            # For collapsible menus, use dbc.Collapse...
        ],
        vertical=True,
        pills=True, # for active link styling
    )
# Note: You still need to define the `*_level_report_layout` functions

def create_report_section():
    return html.Div([
        dbc.Card([
            # Add your chart/tab/table components here...
        ]),
    ])
# Define the main content of the application

def create_main_content():
    return html.Div([
        create_sidebar(),
        main_layout(),
        # Other main content components...
    ], id='main-content', style={'display': 'none'})