# app.py
from dash import html
from app_instance import app
from layouts import create_login_modal, create_sidebar, create_main_content
from callbacks import register_callbacks

# Register the callbacks with the app
register_callbacks(app)

# Define the app layout in a function to make it clear and reusable
def create_app_layout():
    return html.Div([
        create_login_modal(),
        create_sidebar(),
        create_main_content(),
        html.Div(id='main-content', style={'display': 'none'})
    ], className='body-background')

# Set the layout of the app
app.layout = create_app_layout()

if __name__ == '__main__':
    # Turn off debug mode in production!
    app.run_server(debug=False)
