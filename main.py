# Import necessary libraries
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import numpy as np
import plotly.graph_objs as go
from scipy.optimize import fsolve

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div(
    style={'backgroundColor': '#1f1f1f', 'color': 'white', 'fontFamily': 'Arial, sans-serif'},
    children=[
        # Navigation bar with the project title
        html.Nav(
            children=[
                html.Div(
                    children=[
                        html.H1("Syed's Aircraft Performance Project", style={'color': '#6a0dad'}),
                    ],
                    className='navbar',
                    style={'textAlign': 'center', 'padding': '1rem', 'backgroundColor': '#000000'}
                )
            ],
            className='navbar'
        ),
        # Input form for the aircraft parameters
        html.Div([
            html.H2('Input Parameters', style={'color': '#6a0dad'}),
            # Input for Parasite Drag Coefficient
            html.Div([
                html.Label('Parasite Drag Coefficient (c_d0):'),
                dcc.Input(id='c_d0', type='number', value=0.0317, step=0.0001, style={'width': '100%', 'padding': '10px', 'margin': '10px 0'}),
            ]),
            # Input for Aspect Ratio
            html.Div([
                html.Label('Aspect Ratio (AR):'),
                dcc.Input(id='AR', type='number', value=5.71, step=0.01, style={'width': '100%', 'padding': '10px', 'margin': '10px 0'}),
            ]),
            # Input for Oswald Efficiency Factor
            html.Div([
                html.Label('Oswald Efficiency Factor (e0):'),
                dcc.Input(id='e0', type='number', value=0.6, step=0.01, style={'width': '100%', 'padding': '10px', 'margin': '10px 0'}),
            ]),
            # Input for Weight
            html.Div([
                html.Label('Weight (w) in pounds:'),
                dcc.Input(id='w', type='number', value=2400, step=1, style={'width': '100%', 'padding': '10px', 'margin': '10px 0'}),
            ]),
            # Input for Brake Horsepower
            html.Div([
                html.Label('Brake Horsepower (bhp):'),
                dcc.Input(id='bhp', type='number', value=180, step=1, style={'width': '100%', 'padding': '10px', 'margin': '10px 0'}),
            ]),
            # Input for Wing Area
            html.Div([
                html.Label('Wing Area (area) in square feet:'),
                dcc.Input(id='area', type='number', value=170, step=1, style={'width': '100%', 'padding': '10px', 'margin': '10px 0'}),
            ]),
            # Input for Propeller Diameter
            html.Div([
                html.Label('Propeller Diameter (prop_diameter) in feet:'),
                dcc.Input(id='prop_diameter', type='number', value=73/12, step=0.1, style={'width': '100%', 'padding': '10px', 'margin': '10px 0'}),
            ]),
            # Input for RPM
            html.Div([
                html.Label('RPM:'),
                dcc.Input(id='rpm', type='number', value=2700, step=1, style={'width': '100%', 'padding': '10px', 'margin': '10px 0'}),
            ]),
            # Calculate button
            html.Button('Calculate', id='calculate', n_clicks=0, style={'backgroundColor': '#6a0dad', 'color': 'white', 'border': 'none', 'padding': '15px 32px', 'textAlign': 'center', 'fontSize': '16px', 'margin': '10px 0'}),
        ], className='input-form'),
        # Output div for displaying the plots
        html.Div(id='output-div')
    ]
)

# Callback function to update the output based on input parameters
@app.callback(
    Output('output-div', 'children'),
    Input('calculate', 'n_clicks'),
    State('c_d0', 'value'),
    State('AR', 'value'),
    State('e0', 'value'),
    State('w', 'value'),
    State('bhp', 'value'),
    State('area', 'value'),
    State('prop_diameter', 'value'),
    State('rpm', 'value'),
)
def update_output(n_clicks, c_d0, AR, e0, w, bhp, area, prop_diameter, rpm):
    if n_clicks == 0:
        return ''
    
    # Constants for air density at different altitudes
    density = 2.377 * 10**-3
    density_5000ft = 2.048 * 10**-3
    density_10000ft = 1.756 * 10**-3
    density_15000ft = 1.496 * 10**-3
    density_ratios = [1, 0.86159, 0.738746, 0.62936]
    
    # Lift coefficient range
    c_l = np.linspace(0, 1.3182, 20)
    # Convert bhp to watts (1 hp = 550 watts)
    bhp *= 550
    # Air densities for different altitudes
    rpms = [density, density_5000ft, density_10000ft, density_15000ft]

    # Function to calculate values for a given air density
    def calculate_values(density, density_ratio):
        c_d = c_d0 + (c_l**2 / (3.14 * e0 * AR))
        v = np.sqrt(w / (0.5 * density * area)) * (1 / np.sqrt(c_l))
        d = 0.5 * density * area * v**2
        J = v / ((rpm / 60) * prop_diameter)
        prop_efficiency = -12.06 * J**4 + 27.19 * J**3 - 23.08 * J**2 + 9.281 * J - 0.8122
        p_req = w * np.sqrt(2 * w / (area * density)) * (c_d / c_l**1.5)
        shp = bhp * density_ratio
        p_av = shp * prop_efficiency
        roc = (p_av - p_req) / w
        climb_angle = np.arcsin(roc / v)
        return v, roc, climb_angle

    # Calculate values for all specified altitudes
    results = [calculate_values(density, ratio) for density, ratio in zip(rpms, density_ratios)]

    # List to store plots
    plots = []

    # Generate plots for each altitude
    for i, (altitude, density_ratio, (v, roc, climb_angle)) in enumerate(zip([0, 5000, 10000, 15000], density_ratios, results)):
        plots.append(
            dcc.Graph(
                id=f'roc-plot-{i}',
                figure={
                    'data': [
                        go.Scatter(x=v, y=roc, mode='lines', name=f'Rate of Climb at {altitude} ft', line=dict(color='#6a0dad'))
                    ],
                    'layout': go.Layout(
                        title=f'Rate of Climb at {altitude} ft',
                        xaxis={'title': 'Velocity (ft/s)', 'color': 'white'},
                        yaxis={'title': 'Rate of Climb (ft/s)', 'color': 'white'},
                        margin={'l': 40, 'b': 40, 't': 40, 'r': 40},
                        paper_bgcolor='#1f1f1f',
                        plot_bgcolor='#1f1f1f',
                        font={'color': 'white'}
                    )
                }
            )
        )
        plots.append(
            dcc.Graph(
                id=f'climb-angle-plot-{i}',
                figure={
                    'data': [
                        go.Scatter(x=v, y=climb_angle, mode='lines', name=f'Climb Angle at {altitude} ft', line=dict(color='#ff69b4'))
                    ],
                    'layout': go.Layout(
                        title=f'Climb Angle at {altitude} ft',
                        xaxis={'title': 'Velocity (ft/s)', 'color': 'white'},
                        yaxis={'title': 'Climb Angle (radians)', 'color': 'white'},
                        margin={'l': 40, 'b': 40, 't': 40, 'r': 40},
                        paper_bgcolor='#1f1f1f',
                        plot_bgcolor='#1f1f1f',
                        font={'color': 'white'}
                    )
                }
            )
        )

    # Return the generated plots
    return html.Div(plots)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
