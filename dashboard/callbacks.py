# callbacks.py
from dash import Output, Input, State, html
from app_instance import app
from layouts import (
    ue_level_report_layout,
    cell_level_report_layout,
    gnodb_level_report_layout,
    network_level_report_layout
)

def check_credentials(username, password):
    print("Validating credentials") 
    return username == 'admin' and password == 'admin'

def register_callbacks(app):

    @app.callback(
        [Output('login-modal', 'is_open'),
         Output('main-content', 'style'),  
         Output('login-error-message', 'children')],
        [Input('login-button', 'n_clicks')],
        [State('username-input', 'value'),
         State('password-input', 'value')]
    )
    def login_callback(n_clicks, username, password):
        if n_clicks:
            print("Login clicked")

            if check_credentials(username, password):
                print("Login successful")
                return False, {'display': 'block'}, ""
            else:
                return True, {'display': 'none'}, "Incorrect credentials"

        return True, {'display': 'none'}, ""

    @app.callback(
        Output("tab-content", "children"),
        [Input("tabs", "active_tab")]
    )
    def tab_callback(active_tab):
        if active_tab == "tab-ue":
            return ue_level_report_layout()
        elif active_tab == "tab-cell":
            return cell_level_report_layout()
        elif active_tab == "tab-gnodb":
            return gnodb_level_report_layout()
        elif active_tab == "tab-network":
            return network_level_report_layout()
        return html.Div()

register_callbacks(app)
