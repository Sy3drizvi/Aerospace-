import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import pandas as pd
import os

# Load the Excel file
file_path = 'data.xlsx'
excel_data = pd.ExcelFile(file_path)

# Function to format data to three significant figures and drop NaN columns and rows
def format_data(df):
    df = df.dropna(axis=1, how='all')  # Drop columns with all NaN values
    df = df.dropna(axis=0, how='all')  # Drop rows with all NaN values
    for col in df.select_dtypes(include=['float', 'int']).columns:
        df[col] = df[col].apply(lambda x: '{:.3g}'.format(x) if pd.notna(x) else '')  # Format numbers and replace NaN with empty string
    df = df.fillna('')  # Replace any remaining NaN values with an empty string
    return df

# Function to create a DataTable from a DataFrame
def create_table(df):
    df = format_data(df)
    return dash_table.DataTable(
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        style_table={'overflowX': 'auto'},
        style_cell={
            'height': 'auto',
            'minWidth': '100px', 'width': '100px', 'maxWidth': '100px',
            'whiteSpace': 'normal',
            'backgroundColor': 'black',
            'color': 'white'
        },
        style_header={
            'backgroundColor': 'grey',
            'fontWeight': 'bold'
        },
        style_data={
            'backgroundColor': 'black',
            'color': 'white'
        }
    )

# Create the app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Generate tabs with DataTables for each sheet
tabs = []
for sheet_name in excel_data.sheet_names:
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    tabs.append(
        dbc.Tab(label=sheet_name, tab_id=sheet_name, children=[
            html.Div(create_table(df))
        ])
    )

# Create cards to display images
def create_image_card(image_path, index):
    return dbc.Card(
        [
            html.Div(
                dbc.CardImg(src=image_path, top=True, style={'height': '300px', 'objectFit': 'contain', 'cursor': 'pointer'}),
                id=f"image-{index}", n_clicks=0
            )
        ],
        style={'margin': '10px', 'border': 'none'}
    )

# Navbar component
navbar = dbc.Navbar(
    dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(dbc.NavbarBrand("Syed Aircraft Performance Analysis", className="ml-2", style={'color': 'white', 'text-align': 'center', 'font-size': '24px'}))
                ],
                align="center",
                className="g-0"
            ),
        ],
        fluid=True,
    ),
    color="black",
    dark=True,
    className="mb-4"
)

# Image gallery
image_paths = [f"/assets/images/{img}" for img in os.listdir('assets/images') if img.endswith('.png')]
image_gallery = dbc.Container(
    dbc.Row(
        [dbc.Col(create_image_card(image_path, index), width=4) for index, image_path in enumerate(image_paths)],
        justify="center"
    ),
    fluid=True,
)

# Modal for displaying images
modals = [dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle(f"Image {index+1}")),
        dbc.ModalBody(html.Img(src=image_path, style={'width': '100%'})),
        dbc.ModalFooter(
            dbc.Button("Close", id=f"close-{index}", className="ms-auto", n_clicks=0)
        ),
    ],
    id=f"modal-{index}",
    is_open=False,
    size="xl",
) for index, image_path in enumerate(image_paths)]

# Layout of the app
app.layout = dbc.Container([
    navbar,
    dbc.Tabs(id="tabs", active_tab=excel_data.sheet_names[0], children=tabs, className="mt-4"),
    html.Hr(),
    html.H2("Image Gallery", style={'text-align': 'center', 'color': 'white'}),
    image_gallery,
    *modals
], fluid=True, style={'backgroundColor': 'black'})

# Callbacks for opening and closing modals
for index in range(len(image_paths)):
    @app.callback(
        Output(f"modal-{index}", "is_open"),
        [Input(f"image-{index}", "n_clicks"), Input(f"close-{index}", "n_clicks")],
        [State(f"modal-{index}", "is_open")]
    )
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

if __name__ == '__main__':
    app.run_server(debug=True)
